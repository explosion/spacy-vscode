/* -------------------------------------------------------------------------
 * Original work Copyright (c) Microsoft Corporation. All rights reserved.
 * Original work licensed under the MIT License.
 * See ThirdPartyNotices.txt in the project root for license information.
 * All modifications Copyright (c) Open Law Library. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http: // www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ----------------------------------------------------------------------- */
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
const importPython = "'import pygls; import spacy'"

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

function startLangServerTCP(addr: number): LanguageClient {
    const serverOptions: ServerOptions = () => {
        return new Promise((resolve /*, reject */) => {
            const clientSocket = new net.Socket();
            clientSocket.connect(addr, "127.0.0.1", () => {
                resolve({
                    reader: clientSocket,
                    writer: clientSocket,
                });
            });
        });
    };

    return new LanguageClient(
        `tcp lang server (port ${addr})`,
        serverOptions,
        clientOptions
    );
}

function startLangServer(
    command: string,
    args: string[],
    cwd: string
): LanguageClient {
    const serverOptions: ServerOptions = {
        args,
        command,
        options: { cwd },
    };

    return new LanguageClient(command, serverOptions, clientOptions);
}

async function startProduction() {
    const cwd = path.join(__dirname, "..", "..");
    let pythonPath: string = await vscode.commands.executeCommand('python.interpreterPath', { workspaceFolder: cwd })
    let pythonEnvVerified = await verifyPythonEnvironment(pythonPath)
    console.log(pythonEnvVerified)
    if (pythonEnvVerified) {
        vscode.window.showInformationMessage("Server started on" + pythonPath)
        return startLangServer(pythonPath + "", ["-m", "server"], cwd)
    } else {
        vscode.window.showInformationMessage("Server Did Not Start")
        return null;
    }
}

async function verifyPythonEnvironment(pythonPath: string): Promise<Boolean> {
    try {
        const { stdout, stderr } = await exec(pythonPath + " -c " + importPython);
        return true;
    } catch (e) {
        return false;
    }
}

export async function activate(context: ExtensionContext) {

    vscode.window.showInformationMessage("spaCy Extension Activated!")

    client = await startProduction()



    // let showPythonEnvironment = vscode.commands.registerCommand("spacy.showCurrentEnv", async () => {
    //     const cwd = path.join(__dirname, "..", "..");
    //     let pythonPath = await vscode.commands.executeCommand('python.interpreterPath', { workspaceFolder: cwd })
    //     vscode.window.showInformationMessage(pythonPath + "")

    // })
    // context.subscriptions.push(showPythonEnvironment)

    if (context.extensionMode === ExtensionMode.Development) {
        // Development - Run the server manually
        // client = startLangServerTCP(2087)
    } else {
        // Production - Client is going to run the server (for use within `.vsix` package)
        //client = startProduction()
    }

    // context.subscriptions.push(
    //     onDidChangePythonInterpreter(async () => {
    //         vscode.window.showInformationMessage("Python Environment Changed!")
    //         const cwd = path.join(__dirname, "..", "..");
    //         let pythonPath = await vscode.commands.executeCommand('python.interpreterPath', { workspaceFolder: cwd })
    //         vscode.window.showInformationMessage(pythonPath + "")
    //     }),
    // );

    // const api = await getPythonExtensionAPI();

    // if (api) {
    //     console.log("API TIME?")
    //     context.subscriptions.push(
    //         api.environments.onDidChangeActiveEnvironmentPath((e) => {
    //             onDidChangePythonInterpreterEvent.fire({ path: [e.path], resource: e.resource?.uri });
    //         }),
    //     );
    // }

    //const cwd = path.join(__dirname, "..", "..");
    //vscode.commands.executeCommand('python.interpreterPath', { workspaceFolder: cwd }).then(async (pythonPath) => {
    //    client = startLangServer(pythonPath + "", ["-m", "server"], cwd);
    //    await client.start()
    //}).then(undefined, console.error);
}

export function deactivate(): Thenable<void> {
    vscode.window.showInformationMessage("spaCy Extension Deactivated!")
    return client ? client.stop() : Promise.resolve();
}

