import * as vscode from 'vscode';

/**
 * Behavioral signal collection — per-developer, local only.
 *
 * Signals (Phase 4+):
 * - Active reading time (cursor in file, window focused, not idle)
 * - AI completion acceptance without edits
 * - Score decay as code changes
 */
export class Tracker implements vscode.Disposable {
  private disposables: vscode.Disposable[] = [];

  constructor(private readonly dataDir: string) {
    // TODO: persist signals to {workspace}/.fathom/signals.json
  }

  dispose(): void {
    this.disposables.forEach((d) => d.dispose());
  }
}
