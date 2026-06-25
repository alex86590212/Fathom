import * as vscode from 'vscode';
import {
  findTestsRoot,
  isTestFile,
  runCheck,
  runScore,
  type FathomReport,
} from './analyzer';
import { Heatmap } from './heatmap';
import { MatrixPanel } from './matrixPanel';
import { persistReport } from './persist';

let heatmap: Heatmap | undefined;
let lastReport: FathomReport | undefined;
let statusBar: vscode.StatusBarItem | undefined;

async function refreshEditor(context: vscode.ExtensionContext): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    return;
  }

  const filePath = editor.document.uri.fsPath;
  if (!filePath.endsWith('.py')) {
    statusBar?.hide();
    return;
  }

  try {
    if (isTestFile(filePath) && lastReport) {
      heatmap?.refreshActiveEditor();
      const file = lastReport.files.find((f) => f.path === filePath);
      if (file && statusBar) {
        statusBar.text = `$(eye) Fathom: ${file.risk_zone}`;
        statusBar.tooltip = `Honesty ${file.test_honesty_score.toFixed(0)} · Comprehension ${file.comprehension_score.toFixed(0)}`;
        statusBar.show();
      }
    } else if (!isTestFile(filePath)) {
      const score = await runScore(filePath);
      if (statusBar) {
        statusBar.text = `$(eye) Comprehension: ${score.comprehension_score.toFixed(0)}`;
        statusBar.tooltip = `Origin: ${score.origin}`;
        statusBar.show();
      }
      heatmap?.clear(editor);
    }
  } catch {
    statusBar?.hide();
  }
}

async function runFullCheck(context: vscode.ExtensionContext): Promise<void> {
  const testsPath = findTestsRoot();
  if (!testsPath) {
    void vscode.window.showErrorMessage('Fathom: no tests/ directory found in workspace');
    return;
  }

  try {
    const report = await runCheck(testsPath);
    lastReport = report;
    persistReport(report);
    heatmap?.updateFromReport(report);
    void vscode.window.showInformationMessage(
      `Fathom: ${report.files_scanned} files, ${report.findings.length} findings`,
    );
    await refreshEditor(context);
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    void vscode.window.showErrorMessage(
      `Fathom: failed to run analyzer. Is fathom on PATH? ${msg}`,
    );
  }
}

export function activate(context: vscode.ExtensionContext): void {
  heatmap = new Heatmap();
  statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  context.subscriptions.push(heatmap, statusBar);

  context.subscriptions.push(
    vscode.commands.registerCommand('fathom.check', () => runFullCheck(context)),
    vscode.commands.registerCommand('fathom.showMatrix', () => {
      if (!lastReport) {
        void vscode.window.showWarningMessage('Run Fathom: Check first');
        return;
      }
      MatrixPanel.show(context, lastReport);
    }),
    vscode.window.onDidChangeActiveTextEditor(() => refreshEditor(context)),
  );

  void runFullCheck(context);
}

export function deactivate(): void {
  heatmap?.dispose();
  statusBar?.dispose();
}
