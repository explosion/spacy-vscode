"use strict";

import * as net from "net";
import * as path from "path";
import { ExtensionContext, ExtensionMode, workspace } from "vscode";
import * as vscode from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
} from "vscode-languageclient/node";
import { exec } from "child_process";
import { compare } from "compare-versions";

import {
  spacy_version,
  pygls_version,
  python_import,
} from "./client_constants";

const fs = require("fs");

// Server
let client: LanguageClient;

import { platform } from 'node:process';

let pythonPathSuffix = "/bin/python"
if(platform == "win32"){
  pythonPathSuffix = "/Scripts/python.exe"
}

// Status Logging
let logging: vscode.LogOutputChannel;
let statusBar: vscode.StatusBarItem;
let clientActive: boolean = false;

// Environment Compatibility
let currentPythonEnvironment: string = "None";

const clientOptions: LanguageClientOptions = {
  // Register the server for .cfg files
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

// Server Functionality
function startLangServer(
  command: string,
  args: string[],
  cwd: string
): LanguageClient {
  /**
   * Starts the client server
   */
  const serverOptions: ServerOptions = {
    args,
    command,
    options: { cwd },
  };
  logging.info("Client started on: " + currentPythonEnvironment);
  return new LanguageClient(command, serverOptions, clientOptions);
}

async function startProduction() {
  /**
   * Starts the client and python server
   * @returns LanguageClient
   */
  const cwd = path.join(__dirname, "..", "..");

  if (currentPythonEnvironment == "") {
    showServerStatus();
  }
  // Check whether active python environment has all modules installed (pygls, spacy)
  let pythonEnvVerified = await verifyPythonEnvironment(
    currentPythonEnvironment
  );
  if (pythonEnvVerified) {
    return startLangServer(
      currentPythonEnvironment + "",
      ["-m", "server"],
      cwd
    );
  }
}

async function restartClient() {
  // Restart the server
  logging.info("Restarting Server");
  if (client) {
    await client.stop();
    setStatus(false);
  }
  client = await startProduction();
  if (client) {
    await client.start();
    setStatus(true);
  }
}

async function showServerStatus() {
  // Return current status of the server and enable user to select new interpreter
  const options: vscode.MessageOptions = { detail: "", modal: false };
  const option_1 = "Select interpreter";
  const option_2 = "Select current interpreter";

  let message: string;
  let selection: string;
  let pythonPath: string;
  let cwd = path.join(__dirname, "..", "..");

  if (clientActive) {
    message = "spaCy extension active on " + currentPythonEnvironment;
  } else if (currentPythonEnvironment == "") {
    message = "Please select a python interpreter";
  }

  selection = await vscode.window.showInformationMessage(
    message,
    options,
    ...[option_1, option_2]
  );

  if (selection == option_1) {
    // Select python interpreter from file system
    let uris = await vscode.window.showOpenDialog({
      filters: {},
      canSelectFiles: false,
      canSelectFolders: true,
      canSelectMany: false,
      openLabel: "Select python interpreter",
    });
    if (uris) {
      pythonPath = uris[0].fsPath + pythonPathSuffix;
    }
  } else if (selection == option_2) {
    // Select current python interpreter
    pythonPath = await vscode.commands.executeCommand(
      "python.interpreterPath",
      { workspaceFolder: cwd }
    );
  }

  if (pythonPath) {
    let pythonSet = await setPythonEnvironment(pythonPath);
    if (pythonSet) {
      restartClient();
    } else {
      vscode.window.showWarningMessage(
        "Python Interpreter Selected Is Not Compatible"
      );
    }
  }
}

// Python Functionality
async function setPythonEnvironment(pythonPath: string) {
  let env_compatible = await verifyPythonEnvironment(pythonPath);
  if (env_compatible) {
    logging.info("Interpreter compatible: " + pythonPath);
    currentPythonEnvironment = pythonPath;
    return true;
  } else {
    logging.warn("Interpreter not compatible: " + pythonPath);
    return false;
  }
}

async function verifyPythonEnvironment(pythonPath: string): Promise<boolean> {
  /**
   * Runs a child process to verify whether the selected python environment has all modules
   * @param pythonPath - Path to the python environment
   * @returns Promise<Boolean>
   */
  if (fs.existsSync(pythonPath)) {
    return await importPythonCommand(pythonPath + " -c " + '"' + python_import + '"');
  }
  return new Promise((resolve, reject) => {
    logging.error("Selected python interpreter does not exist: " + pythonPath);
    resolve(false);
  });
}

function importPythonCommand(cmd): Promise<boolean> {
  /**
   * Starts a child process and runs the python import command
   * Handles whether python modules are missing or the wrong versions are installed
   * @param cmd: string - Import command to execute
   * @returns Promise<Boolean>
   */
  return new Promise((resolve, reject) => {
    exec(cmd, (error, stdout, stderr) => {
      if (error) {
        if (error.message.includes("ModuleNotFoundError:")) {
          let moduleNotFound = error.message
            .split("ModuleNotFoundError:")[1]
            .trim();
          logging.error(
            "Selected python interpreter has missing modules required to run the extension: " +
              moduleNotFound
          );
        } else {
          logging.error(
            "Error when checking python interpreter: " + error.message
          );
        }
        resolve(false);
      }
      // Check if module versions are compatible
      let module_versions = stdout.split(" ");
      if (
        compare(pygls_version, module_versions[0].trim(), ">=") &&
        compare(spacy_version, module_versions[1].trim(), ">=")
      ) {
        resolve(true);
      } else {
        logging.error(
          "Module versions not compatible: pygls " +
            module_versions[0].trim() +
            " >= " +
            pygls_version +
            " | spaCy " +
            module_versions[1].trim() +
            " >= " +
            spacy_version
        );
        resolve(false);
      }
    });
  });
}

// Helper Functions
function setupStatusBar() {
  // Setup Status Bar
  statusBar = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Right,
    100
  );
  statusBar.command = "spacy-extension.showStatus";
  statusBar.color = "red";
  statusBar.tooltip = "Get the status of the spaCy Extension";
  statusBar.text = "spaCy";
  statusBar.show();

  return statusBar;
}

function setStatus(b: boolean) {
  /**
   * Set the status bar color depending whether the client is active or not
   * @params b: boolean - Is Client Active?
   */
  clientActive = b;
  if (clientActive) {
    statusBar.color = "white";
  } else {
    statusBar.color = "red";
  }
}

export async function activate(context: ExtensionContext) {
  logging = vscode.window.createOutputChannel("spaCy Extension Log", {
    log: true,
  });
  logging.show();

  // Check if Python Extension is installed
  if (!vscode.extensions.getExtension("ms-python.python")) {
    logging.error("python extension not installed");
    return null;
  }

  let _showStatus = vscode.commands.registerCommand(
    "spacy-extension.showStatus",
    showServerStatus
  );
  context.subscriptions.push(_showStatus);

  context.subscriptions.push(setupStatusBar());

  // Start Client
  if (context.extensionMode === ExtensionMode.Development) {
    // Development - Run the server manually
    let settings = require("../../.vscode/settings.json");
    currentPythonEnvironment =
      settings["python.defaultInterpreterPath"] + pythonPathSuffix;
  } else {
    // Production - Client is going to run the server (for use within `.vsix` package)
    currentPythonEnvironment = workspace
      .getConfiguration("spacy-extension")
      .get("defaultPythonInterpreter");
    setPythonEnvironment(currentPythonEnvironment);
  }

  client = await startProduction();

  if (client) {
    await client.start();
    setStatus(true);
  }
}

export function deactivate(): Thenable<void> {
  vscode.window.showInformationMessage("spaCy Extension Deactivated");
  setStatus(false);
  statusBar.hide();
  return client ? client.stop() : Promise.resolve();
}
