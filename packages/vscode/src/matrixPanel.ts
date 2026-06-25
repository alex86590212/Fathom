import * as vscode from 'vscode';
import type { FathomReport, RiskZone } from './analyzer';

export class MatrixPanel {
  private static current: MatrixPanel | undefined;
  private readonly panel: vscode.WebviewPanel;

  private constructor(panel: vscode.WebviewPanel) {
    this.panel = panel;
  }

  static show(context: vscode.ExtensionContext, report: FathomReport): void {
    if (MatrixPanel.current) {
      MatrixPanel.current.panel.reveal();
      MatrixPanel.current.render(report);
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      'fathomMatrix',
      'Fathom Risk Matrix',
      vscode.ViewColumn.Beside,
      { enableScripts: true },
    );
    MatrixPanel.current = new MatrixPanel(panel);
    panel.onDidDispose(() => {
      MatrixPanel.current = undefined;
    });
    panel.webview.onDidReceiveMessage((msg) => {
      if (msg.command === 'open' && msg.path) {
        void vscode.window.showTextDocument(vscode.Uri.file(msg.path));
      }
    });
    MatrixPanel.current.render(report);
    context.subscriptions.push(panel);
  }

  private render(report: FathomReport): void {
    const zones: RiskZone[] = ['critical', 'fragile', 'blind_spot', 'healthy'];
    const byZone = Object.fromEntries(zones.map((z) => [z, [] as typeof report.files])) as Record<
      RiskZone,
      typeof report.files
    >;
    for (const file of report.files) {
      byZone[file.risk_zone].push(file);
    }

    const cells = zones
      .map((zone) => {
        const items = byZone[zone]
          .map(
            (f) =>
              `<li><a href="#" data-path="${f.path}">${f.path.split(/[/\\]/).pop()} (${f.test_honesty_score.toFixed(0)}/${f.comprehension_score.toFixed(0)})</a></li>`,
          )
          .join('');
        return `<div class="cell ${zone}"><h3>${zone}</h3><ul>${items || '<li class="empty">—</li>'}</ul></div>`;
      })
      .join('');

    this.panel.webview.html = `<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: var(--vscode-font-family); color: var(--vscode-foreground); padding: 1rem; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
    .cell { border: 1px solid var(--vscode-panel-border); padding: 0.75rem; border-radius: 6px; }
    .critical { border-left: 4px solid #e06c75; }
    .fragile { border-left: 4px solid #e5c07b; }
    .blind_spot { border-left: 4px solid #61afef; }
    .healthy { border-left: 4px solid #98c379; }
    a { color: var(--vscode-textLink-foreground); }
    .empty { opacity: 0.5; }
  </style>
</head>
<body>
  <h2>Risk Matrix</h2>
  <p>${report.files_scanned} test files · ${report.findings.length} findings</p>
  <div class="grid">${cells}</div>
  <script>
    const vscode = acquireVsCodeApi();
    document.querySelectorAll('a[data-path]').forEach((a) => {
      a.addEventListener('click', (e) => {
        e.preventDefault();
        vscode.postMessage({ command: 'open', path: a.dataset.path });
      });
    });
  </script>
</body>
</html>`;
  }
}
