import * as vscode from 'vscode';
import { Heatmap } from './heatmap';
import { Tracker } from './tracker';
import { Explainer } from './explainer';

let tracker: Tracker | undefined;
let heatmap: Heatmap | undefined;
let explainer: Explainer | undefined;

export function activate(context: vscode.ExtensionContext): void {
  const config = vscode.workspace.getConfiguration('fathom');
  const dataDir = config.get<string>('dataDir', '.fathom');

  tracker = new Tracker(dataDir);
  heatmap = new Heatmap();
  explainer = new Explainer(config.get<string>('claudeApiKey', ''));

  context.subscriptions.push(
    vscode.commands.registerCommand('fathom.check', () => {
      vscode.window.showInformationMessage('Fathom: test honesty check (not yet implemented)');
    }),
    vscode.commands.registerCommand('fathom.showMatrix', () => {
      vscode.window.showInformationMessage('Fathom: risk matrix (not yet implemented)');
    }),
    tracker,
    heatmap,
  );

  // Phase 3: activate tracker on file open/focus
  // Phase 4: heatmap decorations from git origin + behavioral scores
}

export function deactivate(): void {
  tracker?.dispose();
  heatmap?.dispose();
}
