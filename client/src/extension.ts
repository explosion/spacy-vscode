"use strict";

import * as path from "path";
import { ExtensionContext, ExtensionMode, workspace } from "vscode";
import * as vscode from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
} from "vscode-languageclient/node";
import { exec } from "child_process";

import {
  python_args,
  warnings, // eslint-disable-line
  infos,
  errors,
  status,
} from "./client_constants";

import * as fs from "fs"; // eslint-disable-line

// Server
let client: LanguageClient;

// Status Logging
const logging = vscode.window.createOutputChannel("spaCy Extension Log", {
  log: true,
});
logging.show();

let statusBar: vscode.StatusBarItem;
let clientActive = false;

// Environment Compatibility
let currentPythonEnvironment = "None";

const clientOptions: LanguageClientOptions = {
  // Register the server for .cfg files
  documentSelector: [
    { scheme: "file", pattern: "**/*.cfg" },
    { scheme: "untitled", pattern: "**/*.cfg" },
  ],
  outputChannel: logging,
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
  return new LanguageClient(command, serverOptions, clientOptions);
}

async function startProduction() {
  /**
   * Starts the client and python server
   * @returns LanguageClient
   */
  const cwd = path.join(__dirname, "..", "..");
  // Check whether active python environment has all modules installed (pygls, spacy)
  const python_interpreter_compat = await verifyPythonEnvironment(
    currentPythonEnvironment
  );
  if (python_interpreter_compat.includes("I")) {
    return startLangServer(
      currentPythonEnvironment + "",
      ["-m", "server"],
      cwd
    );
  } else {
    showServerStatus();
  }
}

async function restartClient() {
  // Restart the server
  if (client) {
    await client.stop();
    setClientActiveStatus(false);
  }
  client = await startProduction();
  if (client) {
    await client.start();
    setClientActiveStatus(true);
  }
}

async function showServerStatus() {
  // Return current status of the server and enable user to select new interpreter
  const options: vscode.MessageOptions = { detail: "", modal: false };
  const option_select_interpreter = "Select interpreter";
  const option_current_interpreter = "Select current interpreter";

  let message: string;
  let pythonPath: string;
  const cwd = path.join(__dirname, "..", "..");

  if (clientActive) {
    message = status["S001"] + currentPythonEnvironment;
  } else {
    message = status["S002"];
  }

  const selection = await vscode.window.showInformationMessage(
    message,
    options,
    ...[option_select_interpreter, option_current_interpreter]
  );

  if (selection == option_select_interpreter) {
    // Select python interpreter from file system
    logging.info("Selecting from Python Interpreter from Directory");
    const uris = await vscode.window.showOpenDialog({
      filters: {},
      canSelectFiles: false,
      canSelectFolders: true,
      canSelectMany: false,
      openLabel: "Select python interpreter",
    });
    if (uris) {
      pythonPath = getPythonExec(uris[0].fsPath);
    }
  } else if (selection == option_current_interpreter) {
    // Select current python interpreter
    logging.info("Selecting current Python Interpreter");
    pythonPath = await vscode.commands.executeCommand(
      "python.interpreterPath",
      { workspaceFolder: cwd }
    );
  }

  if (pythonPath) {
    logging.info("Python Path retrieved: " + pythonPath);
    const pythonSet = await setPythonEnvironment(pythonPath);
    if (pythonSet) {
      restartClient();
    } else {
      vscode.window.showWarningMessage(status["S003"]);
    }
  } else {
    logging.info("Python Path could not be retrieved");
  }
}

function getAllFiles(dir: string, _files: string[] = []): string[] {
  /** Get all files and sub-files from a directory */
  const filter = ["bin", "Scripts", "shims"];
  _files = _files || [];
  const files = fs.readdirSync(dir);
  for (const i in files) {
    const name = dir + "/" + files[i];
    if (fs.statSync(name).isDirectory() && filter.includes(files[i])) {
      getAllFiles(name, _files);
    } else if (files[i].includes("python")) {
      _files.push(name);
    }
  }
  return _files;
}

function getPythonExec(dir: string): string {
  /** Return path of python executable of a list of files */
  const files = getAllFiles(dir, []);
  for (const i in files) {
    if (files[i].endsWith("python") || files[i].endsWith("python.exe")) {
      return files[i];
    }
  }
  return dir;
}

// Python Functionality
async function setPythonEnvironment(pythonPath: string) {
  /**
   * Verify python environment and set it as currentPythonEnvironment and make it persistent
   * @param pythonPath - Path to the interpreter
   * @returns boolean - Whether the verification succeeded or failed
   */
  if (!fs.existsSync(pythonPath)) {
    logging.error(errors["E003"] + pythonPath);
    return false;
  }
  const python_interpreter_compat = await verifyPythonEnvironment(pythonPath);
  if (python_interpreter_compat.includes("E")) {
    logging.error(errors[python_interpreter_compat]);
    return false;
  } else if (python_interpreter_compat.includes("I")) {
    currentPythonEnvironment = pythonPath;
    workspace
      .getConfiguration("spacy-extension")
      .update("pythonInterpreter", currentPythonEnvironment);
    logging.info(infos[python_interpreter_compat] + currentPythonEnvironment);
    return true;
  } else {
    logging.error(errors["E010"]);
    return false;
  }
}

async function verifyPythonEnvironment(pythonPath: string): Promise<string> {
  /**
   * Runs a child process to verify whether the selected python environment has all modules
   * @param pythonPath - Path to the python environment
   * @returns Promise<Boolean>
   */

  return await importPythonCommand(
    pythonPath +
      ` ${path.join(
        __dirname,
        "..",
        "..",
        "client",
        "python_validation.py"
      )} ` +
      python_args
  );
}

function importPythonCommand(cmd): Promise<string> {
  /**
   * Starts a child process and runs the python import command
   * Handles whether python modules are missing or the wrong versions are installed
   * @param cmd: string - Import command to execute
   * @returns Promise<Boolean>
   */
  return new Promise((resolve, reject) => {
    exec(cmd, (error, stdout, stderr) => {
      resolve(stdout);
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

function setClientActiveStatus(b: boolean) {
  /**
   * Set the status bar color depending whether the client is active or not
   * @params b: boolean - Is Client Active?
   */
  clientActive = b;
  if (clientActive) {
    statusBar.color = new vscode.ThemeColor("activityBar.foreground");
    logging.info(infos["I001"]);
  } else {
    statusBar.color = "red";
    logging.info(infos["I002"]);
  }
}

export async function activate(context: ExtensionContext) {
  // Check if Python Extension is installed
  if (!vscode.extensions.getExtension("ms-python.python")) {
    logging.error(errors["E001"]);
    return null;
  }

  const _showStatus = vscode.commands.registerCommand(
    "spacy-extension.showStatus",
    showServerStatus
  );
  context.subscriptions.push(_showStatus);

  context.subscriptions.push(setupStatusBar());

  // Start Client
  if (context.extensionMode === ExtensionMode.Development) {
    // Development
    const settings = require("../../.vscode/settings.json"); // eslint-disable-line
    currentPythonEnvironment = getPythonExec(
      settings["python.defaultInterpreterPath"]
    );
  } else {
    // Production
    currentPythonEnvironment = workspace
      .getConfiguration("spacy-extension")
      .get("pythonInterpreter");
  }

  await setPythonEnvironment(currentPythonEnvironment);
  client = await startProduction();

  if (client) {
    await client.start();
    setClientActiveStatus(true);
  }
}

export function deactivate(): Thenable<void> {
  setClientActiveStatus(false);
  statusBar.hide();
  return client ? client.stop() : Promise.resolve();
}
