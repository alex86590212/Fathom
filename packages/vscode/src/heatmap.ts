import * as vscode from 'vscode';

export type RiskZone = 'critical' | 'fragile' | 'blind_spot' | 'healthy';

const ZONE_COLORS: Record<RiskZone, string> = {
  critical: 'fathom.critical',
  fragile: 'fathom.fragile',
  blind_spot: 'fathom.blindSpot',
  healthy: 'fathom.healthy',
};

/**
 * Gutter decorations showing comprehension × test honesty risk zones.
 * Phase 3: heatmap from git history alone.
 * Phase 4: combined with behavioral tracking scores.
 */
export class Heatmap implements vscode.Disposable {
  private decorationTypes = new Map<RiskZone, vscode.TextEditorDecorationType>();

  constructor() {
    for (const [zone, colorKey] of Object.entries(ZONE_COLORS)) {
      this.decorationTypes.set(
        zone as RiskZone,
        vscode.window.createTextEditorDecorationType({
          gutterIconPath: undefined, // TODO: zone-specific gutter icons
          overviewRulerColor: new vscode.ThemeColor(colorKey),
          overviewRulerLane: vscode.OverviewRulerLane.Right,
        }),
      );
    }
  }

  /** Apply risk zone decorations to the active editor. (Not yet implemented.) */
  update(editor: vscode.TextEditor, zones: Map<number, RiskZone>): void {
    // TODO: map line numbers to decoration types
  }

  dispose(): void {
    this.decorationTypes.forEach((dt) => dt.dispose());
  }
}
