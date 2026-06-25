import * as vscode from 'vscode';
import type { FathomReport, RiskZone } from './analyzer';

const ZONE_COLORS: Record<RiskZone, string> = {
  critical: 'fathom.critical',
  fragile: 'fathom.fragile',
  blind_spot: 'fathom.blindSpot',
  healthy: 'fathom.healthy',
};

export class Heatmap implements vscode.Disposable {
  private decorationTypes = new Map<RiskZone, vscode.TextEditorDecorationType>();
  private fileZones = new Map<string, RiskZone>();

  constructor() {
    for (const [zone, colorKey] of Object.entries(ZONE_COLORS)) {
      this.decorationTypes.set(
        zone as RiskZone,
        vscode.window.createTextEditorDecorationType({
          backgroundColor: new vscode.ThemeColor(`${colorKey}33`),
          overviewRulerColor: new vscode.ThemeColor(colorKey),
          overviewRulerLane: vscode.OverviewRulerLane.Full,
          isWholeLine: true,
        }),
      );
    }
  }

  updateFromReport(report: FathomReport): void {
    this.fileZones.clear();
    for (const file of report.files) {
      this.fileZones.set(file.path, file.risk_zone);
    }
    this.refreshActiveEditor();
  }

  refreshActiveEditor(): void {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      return;
    }
    const zone = this.fileZones.get(editor.document.uri.fsPath);
    if (!zone) {
      this.clear(editor);
      return;
    }
    const deco = this.decorationTypes.get(zone);
    if (!deco) {
      return;
    }
    const lineCount = editor.document.lineCount;
    const range = new vscode.Range(0, 0, lineCount, 0);
    editor.setDecorations(deco, [range]);
    for (const [z, dt] of this.decorationTypes) {
      if (z !== zone) {
        editor.setDecorations(dt, []);
      }
    }
  }

  clear(editor: vscode.TextEditor): void {
    for (const dt of this.decorationTypes.values()) {
      editor.setDecorations(dt, []);
    }
  }

  dispose(): void {
    this.decorationTypes.forEach((dt) => dt.dispose());
  }
}
