import * as path from 'path';
import * as vscode from 'vscode';
import type { FileReport, FathomReport, RiskZone } from './analyzer';

const ZONE_COLORS: Record<RiskZone, string> = {
  critical: 'fathom.critical',
  fragile: 'fathom.fragile',
  blind_spot: 'fathom.blindSpot',
  healthy: 'fathom.healthy',
};

const ZONE_LABELS: Record<RiskZone, string> = {
  critical: 'Critical risk',
  fragile: 'Fragile confidence',
  blind_spot: 'Blind spot',
  healthy: 'Healthy',
};

export function pathsEqual(a: string, b: string): boolean {
  return path.normalize(a) === path.normalize(b);
}

export function formatFindingHover(
  finding: FileReport['findings'][0],
  file: FileReport,
): vscode.MarkdownString {
  const md = new vscode.MarkdownString();
  md.isTrusted = true;
  md.supportHtml = false;
  md.appendMarkdown(`### Fathom · ${ZONE_LABELS[file.risk_zone]}\n\n`);
  md.appendMarkdown(`**Pattern:** \`${finding.pattern}\`\n\n`);
  md.appendMarkdown(`${finding.message}\n\n`);
  md.appendMarkdown(
    `Honesty **${file.test_honesty_score.toFixed(0)}** · ` +
      `Comprehension **${file.comprehension_score.toFixed(0)}** · ` +
      `Origin \`${file.origin}\``,
  );
  return md;
}

export function formatFileHover(file: FileReport): vscode.MarkdownString {
  const md = new vscode.MarkdownString();
  md.isTrusted = true;
  md.appendMarkdown(`### Fathom · ${ZONE_LABELS[file.risk_zone]}\n\n`);
  md.appendMarkdown(
    `Honesty **${file.test_honesty_score.toFixed(0)}** · ` +
      `Comprehension **${file.comprehension_score.toFixed(0)}**\n\n`,
  );
  md.appendMarkdown(`Origin: \`${file.origin}\`\n\n`);
  if (file.findings.length === 0) {
    md.appendMarkdown('_No dishonest test patterns in this file._');
  } else {
    md.appendMarkdown(`**${file.findings.length} finding(s)** — hover flagged lines for details.`);
  }
  return md;
}

export class Heatmap implements vscode.Disposable {
  private zoneDecorations = new Map<RiskZone, vscode.TextEditorDecorationType>();
  private findingDecoration: vscode.TextEditorDecorationType;
  private fileReports = new Map<string, FileReport>();

  constructor() {
    for (const [zone, colorKey] of Object.entries(ZONE_COLORS)) {
      this.zoneDecorations.set(
        zone as RiskZone,
        vscode.window.createTextEditorDecorationType({
          overviewRulerColor: new vscode.ThemeColor(colorKey),
          overviewRulerLane: vscode.OverviewRulerLane.Left,
          isWholeLine: true,
          borderWidth: '0 0 0 3px',
          borderStyle: 'solid',
          borderColor: new vscode.ThemeColor(colorKey),
        }),
      );
    }

    this.findingDecoration = vscode.window.createTextEditorDecorationType({
      backgroundColor: new vscode.ThemeColor('editor.wordHighlightStrongBackground'),
      overviewRulerColor: new vscode.ThemeColor('fathom.critical'),
      overviewRulerLane: vscode.OverviewRulerLane.Center,
      isWholeLine: true,
    });
  }

  updateFromReport(report: FathomReport): void {
    this.fileReports.clear();
    for (const file of report.files) {
      this.fileReports.set(path.normalize(file.path), file);
    }
    this.refreshActiveEditor();
  }

  getFileReport(filePath: string): FileReport | undefined {
    return this.fileReports.get(path.normalize(filePath));
  }

  refreshActiveEditor(): void {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      return;
    }

    const filePath = path.normalize(editor.document.uri.fsPath);
    const file = this.fileReports.get(filePath);

    if (!file) {
      this.clear(editor);
      return;
    }

    const zoneDeco = this.zoneDecorations.get(file.risk_zone);
    if (zoneDeco) {
      const lastLine = Math.max(0, editor.document.lineCount - 1);
      editor.setDecorations(zoneDeco, [
        {
          range: new vscode.Range(0, 0, lastLine, 0),
          hoverMessage: formatFileHover(file),
        },
      ]);
      for (const [zone, deco] of this.zoneDecorations) {
        if (zone !== file.risk_zone) {
          editor.setDecorations(deco, []);
        }
      }
    }

    const findingDecorations: vscode.DecorationOptions[] = [];
    for (const finding of file.findings) {
      const lineIndex = finding.line - 1;
      if (lineIndex < 0 || lineIndex >= editor.document.lineCount) {
        continue;
      }
      findingDecorations.push({
        range: editor.document.lineAt(lineIndex).range,
        hoverMessage: formatFindingHover(finding, file),
      });
    }
    editor.setDecorations(this.findingDecoration, findingDecorations);
  }

  clear(editor: vscode.TextEditor): void {
    for (const deco of this.zoneDecorations.values()) {
      editor.setDecorations(deco, []);
    }
    editor.setDecorations(this.findingDecoration, []);
  }

  dispose(): void {
    this.zoneDecorations.forEach((deco) => deco.dispose());
    this.findingDecoration.dispose();
  }
}

export function registerHoverProvider(
  context: vscode.ExtensionContext,
  getFileReport: (filePath: string) => FileReport | undefined,
): void {
  context.subscriptions.push(
    vscode.languages.registerHoverProvider('python', {
      provideHover(document, position) {
        const file = getFileReport(document.uri.fsPath);
        if (!file) {
          return null;
        }

        const line = position.line + 1;
        const finding = file.findings.find((f) => f.line === line);
        if (finding) {
          return new vscode.Hover(formatFindingHover(finding, file));
        }

        return new vscode.Hover(formatFileHover(file));
      },
    }),
  );
}
