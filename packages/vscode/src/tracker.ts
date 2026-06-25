import * as vscode from 'vscode';

/**
 * Behavioral signal collection — per-developer, local only. (Phase 4)
 */
export class Tracker implements vscode.Disposable {
  private disposables: vscode.Disposable[] = [];

  constructor(private readonly dataDir: string) {
    // Phase 4: persist signals to {workspace}/.fathom/signals.json
  }

  dispose(): void {
    this.disposables.forEach((d) => d.dispose());
  }
}
