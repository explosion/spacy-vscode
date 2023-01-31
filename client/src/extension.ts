"use strict";

import * as net from "net";
import * as path from "path";
import { ExtensionContext, ExtensionMode, workspace } from "vscode";
import * as vscode from "vscode";
import {
  onDidChangePythonInterpreter,
  getPythonExtensionAPI,
  onDidChangePythonInterpreterEvent,
} from "./common/python";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
} from "vscode-languageclient/node";
import { exec } from "child_process";
import { compare } from "compare-versions";

let client: LanguageClient;

// Status Logging
let logging = vscode.window.createOutputChannel("spaCy Extension Log");
let statusBar: vscode.StatusBarItem;
let clientActive: boolean = false;

// Environment Compatibility
let currentPythonEnvironment: string = "None";
const importPython =
  "'import pygls; import spacy; print(pygls.__version__,spacy.__version__);'";
const spaCy_version = "3.5.0";
const pygls_version = "1.0.0";

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
  },
};

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
  logging.appendLine("spaCy Extension: Attempting Starting Client");
  const cwd = path.join(__dirname, "..", "..");
  // Retrieve path to current active python environment
  let defaultPythonPath: string = workspace
    .getConfiguration("spacy-extension")
    .get("defaultPythonInterpreter");
  let pythonPath: string = "";
  if (defaultPythonPath != "") {
    logging.appendLine(
      "spaCy Extension: Default Python Interpreter Selected: " +
        defaultPythonPath
    );
    pythonPath = defaultPythonPath;
    currentPythonEnvironment = defaultPythonPath;
  } else {
    logging.appendLine(
      "spaCy Extension: Retrieving Selected Python Interpreter"
    );
    pythonPath = await vscode.commands.executeCommand(
      "python.interpreterPath",
      { workspaceFolder: cwd }
    );
    logging.appendLine(
      "spaCy Extension: Retrieved Python Interpreter" + pythonPath
    );
  }
  // Check whether active python environment has all modules installed (pygls, spacy)
  let pythonEnvVerified = await verifyPythonEnvironment(pythonPath);
  logging.appendLine(
    "spaCy Extension: Python Environment Compatible: " + pythonEnvVerified
  );
  if (pythonEnvVerified) {
    if (currentPythonEnvironment != pythonPath && defaultPythonPath == "") {
      currentPythonEnvironment = pythonPath;
    } else {
      logging.appendLine(
        "spaCy Extension: Attempting To Start Client Rejected ( Current: " +
          currentPythonEnvironment +
          " | Python: " +
          pythonPath +
          " | Default: " +
          defaultPythonPath
      );
      return null;
    }
    logging.appendLine(
      "spaCy Extension: Using Python Interpreter: " + currentPythonEnvironment
    );
    return startLangServer(
      currentPythonEnvironment + "",
      ["-m", "server"],
      cwd
    );
  } else {
    logging.appendLine("spaCy Extension: Attempting To Start Client Failed");
    return null;
  }
}

async function verifyPythonEnvironment(pythonPath: string): Promise<boolean> {
  /**
   * Runs a child process to verify whether the selected python environment has all modules
   * @param pythonPath - Path to the python environment
   * @returns Promise<Boolean>
   */
  return await execImportCommand(pythonPath + " -c " + importPython);
}

function execImportCommand(cmd): Promise<boolean> {
  /**
   * Starts a child process and runs a the import command
   * @param cmd: string - Import command to execute
   * @returns Promise<Boolean>
   */
  return new Promise((resolve, reject) => {
    exec(cmd, (error, stdout, stderr) => {
      if (error) {
        logging.appendLine(
          "spaCy Extension: Selected Python Interpreter has missing modules required to run the extension: " +
            error.message
        );
        resolve(false);
      }
      let module_versions = stdout.split(" ");
      // Check if module versions are compatible
      if (
        compare(pygls_version, module_versions[0].trim(), ">=") &&
        compare(spaCy_version, module_versions[1].trim(), ">=")
      ) {
        logging.appendLine(
          "spaCy Extension: Module Versions Compatible: pygls " +
            module_versions[0].trim() +
            " >= " +
            pygls_version +
            " | spaCy " +
            module_versions[1].trim() +
            " >= " +
            spaCy_version
        );
        resolve(true);
      } else {
        logging.appendLine(
          "spaCy Extension: Module Versions Not Compatible: pygls " +
            module_versions[0].trim() +
            " >= " +
            pygls_version +
            " | spaCy " +
            module_versions[1].trim() +
            " >= " +
            spaCy_version
        );
        resolve(false);
      }
    });
  });
}

// Server Commands

function returnCurrentPythonEnvironment() {
  vscode.window.showInformationMessage(currentPythonEnvironment);
}

async function restartServer() {
  logging.appendLine("spaCy Extension: Restarting Server");
  currentPythonEnvironment = "";
  if (client) {
    clientActive = false;
    statusBar.color = "red";
    client.stop().then(async (success) => {
      client = await startProduction();
      if (client) {
        await client.start();
        clientActive = true;
        statusBar.color = "white";
        vscode.window.showInformationMessage(
          "spaCy Extension: Server Restarted"
        );
      }
    });
  } else {
    client = await startProduction();
    if (client) {
      await client.start();
      clientActive = true;
      statusBar.color = "white";
      vscode.window.showInformationMessage("spaCy Extension: Server Restarted");
    }
  }
}

async function showStatus() {
  // Return Current State Of The Client Server
  if (clientActive) {
    vscode.window.showInformationMessage(
      "Active On " + currentPythonEnvironment
    );
  } else {
    vscode.window.showInformationMessage(
      "Not Active On " + currentPythonEnvironment
    );
  }
}

export async function activate(context: ExtensionContext) {
  logging.show();
  logging.appendLine("spaCy Extension: Activated");

  // Register Server Commands
  let _returnCurrentPythonEnvironment = vscode.commands.registerCommand(
    "spacy-extension.pythonInterpreter",
    returnCurrentPythonEnvironment
  );
  context.subscriptions.push(_returnCurrentPythonEnvironment);

  let _restartServer = vscode.commands.registerCommand(
    "spacy-extension.restartServer",
    restartServer
  );
  context.subscriptions.push(_restartServer);

  let _showStatus = vscode.commands.registerCommand(
    "spacy-extension.showStatus",
    showStatus
  );
  context.subscriptions.push(_showStatus);

  // Build Status Bar
  statusBar = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Right,
    100
  );
  statusBar.command = "spacy-extension.showStatus";
  statusBar.color = "red";
  statusBar.tooltip = "Get the status of the spaCy Extension";
  statusBar.text = "spaCy";
  context.subscriptions.push(statusBar);

  statusBar.show();

  logging.appendLine("spaCy Extension: Commands Registered");

  // Register Events

  // Initialize Python Listener
  try {
    const pythonAPI = await getPythonExtensionAPI();
    if (pythonAPI) {
      logging.appendLine("spaCy Extension: Python Listener Initialized");
      context.subscriptions.push(
        pythonAPI.environments.onDidChangeActiveEnvironmentPath((e) => {
          onDidChangePythonInterpreterEvent.fire({
            path: [e.path],
            resource: e.resource?.uri,
          });
        })
      );
    }

    // Restart Server Whenerver Python Interpreter Changes
    context.subscriptions.push(
      onDidChangePythonInterpreter(async () => {
        /**
         * Change the Python Interpreter whenever a change event was triggered.
         * Only change the Interpreter if it's compatible, otherwise stay on the current Interpreter
         */
        logging.appendLine("spaCy Extension: Python Interpreter Changed");
        let _client = await startProduction();
        if (_client) {
          if (client) {
            clientActive = false;
            statusBar.color = "red";
            client.stop().then(async (success) => {
              client = _client;
              clientActive = true;
              statusBar.color = "white";
              await client.start();
            });
          } else {
            client = _client;
            clientActive = true;
            statusBar.color = "white";
            await client.start();
          }
        } else {
          logging.appendLine(
            "spaCy Extension: Server Will Stay On Previous Interpreter: " +
              currentPythonEnvironment
          );
        }
      })
    );

    // Start Client

    if (context.extensionMode === ExtensionMode.Development) {
      // Development - Run the server manually
      //client = startLangServerTCP(2087);
      client = await startProduction();
    } else {
      // Production - Client is going to run the server (for use within `.vsix` package)
      client = await startProduction();
    }

    if (client) {
      logging.appendLine("spaCy Extension: Starting Client Server");
      await client.start();
      clientActive = true;
      statusBar.color = "white";
    }
  } catch (e) {
    // Handle unexpected errors when initializing
    logging.appendLine("spaCy Extension: Something went wrong!");
    logging.appendLine("spaCy Extension: " + e);
  }
}

export function deactivate(): Thenable<void> {
  vscode.window.showInformationMessage("spaCy Extension Deactivated!");
  clientActive = false;
  statusBar.color = "red";
  return client ? client.stop() : Promise.resolve();
}
