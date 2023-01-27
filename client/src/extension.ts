"use strict";

import * as net from "net";
import * as path from "path";
import { ExtensionContext, ExtensionMode, workspace } from "vscode";
import * as vscode from 'vscode';
import {
    onDidChangePythonInterpreter,
    getPythonExtensionAPI,
    onDidChangePythonInterpreterEvent
} from './common/python';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
} from "vscode-languageclient/node";
import { exec } from 'child_process'

let client: LanguageClient;
let logging = vscode.window.createOutputChannel("spaCy Extension Log")
let currentPythonEnvironment: string;
const importPython = "'import pygls; import spacy'"

// Server Functionality

const clientOptions: LanguageClientOptions = {
    // Register the server for plain text documents
    documentSelector: [
        { scheme: "file", pattern: "**/*.cfg" },
        { scheme: "untitled", pattern: "**/*.cfg" },
    ],
    outputChannelName: "[pygls] spaCy-Language-Server",
    synchronize: {
        // Notify the server about file changes to '.clientrc files contain in the workspace
        fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
    }
}

function startLangServerTCP(port: number): LanguageClient {
    /** 
     * Start the client server on TCP, only works if you start the python server seperately (Only for development)
     * @param port - Port number to which the client server listens to
     */
    const serverOptions: ServerOptions = () => {
        return new Promise((resolve /*, reject */) => {
            const clientSocket = new net.Socket();
            clientSocket.connect(port, "127.0.0.1", () => {
                resolve({
                    reader: clientSocket,
                    writer: clientSocket,
                });
            });
        });
    };

    return new LanguageClient(
        `tcp lang server (port ${port})`,
        serverOptions,
        clientOptions
    );
}

function startLangServer(
    command: string,
    args: string[],
    cwd: string
): LanguageClient {
    /**
     * Starts the Client Server
     */
    const serverOptions: ServerOptions = {
        args,
        command,
        options: { cwd },
    };

    return new LanguageClient(command, serverOptions, clientOptions);
}

async function startProduction() {
    /**
     * Starts both the Client Server and the Python Server 
     * @returns LanguageClient
     */
    const cwd = path.join(__dirname, "..", "..");
    // Retrieve path to current active python environment
    let defaultPythonPath: string = workspace.getConfiguration("spacy-extension").get("defaultPythonInterpreter")
    let pythonPath: string = "";
    if (defaultPythonPath != "") {
        logging.appendLine("spaCy Extension: Default Python Interpreter Selected: " + defaultPythonPath)
        pythonPath = defaultPythonPath;
        currentPythonEnvironment = defaultPythonPath;
    } else {
        pythonPath = await vscode.commands.executeCommand('python.interpreterPath', { workspaceFolder: cwd })
    }
    // Check whether active python environment has all modules installed (pygls, spacy)
    let pythonEnvVerified = await verifyPythonEnvironment(pythonPath)
    if (pythonEnvVerified) {
        if (currentPythonEnvironment != pythonPath && defaultPythonPath == "") {
            currentPythonEnvironment = pythonPath;
        } else {
            return null;
        }
        logging.appendLine("spaCy Extension: Uses Python Interpreter: " + currentPythonEnvironment)
        return startLangServer(currentPythonEnvironment + "", ["-m", "server"], cwd)
    } else {
        return null;
    }
}

async function verifyPythonEnvironment(pythonPath: string) {
    /**
     * Runs a child process to verify whether the selected python environment has all modules
     * @param pythonPath - Path to the python environment
     * @returns Promise<Boolean>
     */
    return await execShellCommand(pythonPath + " -c " + importPython);
}

function execShellCommand(cmd) {
    /**
     * Starts a child process and runs a specified command
     * @param cmd: string - Command to execute
     * @returns Promise<Boolean>
     */
    return new Promise((resolve, reject) => {
        exec(cmd, (error, stdout, stderr) => {
            if (error) {
                console.warn("The selected python environment environment is missing modules which are required to run the spacy-extension: " + error.message)
                resolve(false);
            }
            resolve(true);
        });
    });
}

// Server Commands

function returnCurrentPythonEnvironment() {
    vscode.window.showInformationMessage(currentPythonEnvironment)
}

async function restartServer() {
    logging.appendLine("spaCy Extension: Restarting Server")
    if (client) {
        client.stop().then(async (success) => {
            client = await startProduction();
            await client.start()
            vscode.window.showInformationMessage("spaCy Extension: Server Restarted")
        })
    } else {
        client = await startProduction();
        await client.start()
        vscode.window.showInformationMessage("spaCy Extension: Server Restarted")
    }
}

export async function activate(context: ExtensionContext) {

    logging.show()
    logging.appendLine("spaCy Extension: Active")

    // Register Server Commands
    let _returnCurrentPythonEnvironment = vscode.commands.registerCommand("spacy-extension.pythonInterpreter", returnCurrentPythonEnvironment)
    context.subscriptions.push(_returnCurrentPythonEnvironment)

    let _restartServer = vscode.commands.registerCommand("spacy-extension.restartServer", restartServer)
    context.subscriptions.push(_restartServer)

    // Register Events

    // Initialize Python Listener
    const pythonAPI = await getPythonExtensionAPI();
    if (pythonAPI) {
        logging.appendLine("spaCy Extension: Python Listener Initialized")
        context.subscriptions.push(
            pythonAPI.environments.onDidChangeActiveEnvironmentPath((e) => {
                onDidChangePythonInterpreterEvent.fire({ path: [e.path], resource: e.resource?.uri });
            }),
        );
    }

    // Restart Server Whenerver Python Interpreter Changes
    context.subscriptions.push(
        onDidChangePythonInterpreter(async () => {
            logging.appendLine("spaCy Extension: Python Interpreter Changed")
            let _client = await startProduction();
            if (_client) {
                if (client) {
                    client.stop().then(async (success) => {
                        client = _client
                        await client.start();
                    })
                } else {
                    client = _client
                    await client.start();
                }
            } else {
                logging.appendLine("spaCy Extension: Server Will Stay On Previous Interpreter: " + currentPythonEnvironment)
            }
        }),
    );

    // Start Client

    if (context.extensionMode === ExtensionMode.Development) {
        // Development - Run the server manually
        //client = startLangServerTCP(2087)
    } else {
        // Production - Client is going to run the server (for use within `.vsix` package)
        client = await startProduction()
    }

    client = await startProduction()

    if (client) {
        await client.start()
    }

}

export function deactivate(): Thenable<void> {
    vscode.window.showInformationMessage("spaCy Extension Deactivated!")
    return client ? client.stop() : Promise.resolve();
}

