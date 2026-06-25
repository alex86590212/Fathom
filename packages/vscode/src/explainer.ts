import * as vscode from 'vscode';

/**
 * On-demand Claude API explanations for red-zone code. (Phase 4)
 */
export class Explainer {
  constructor(private readonly apiKey: string) {}

  async explain(filePath: string, line: number): Promise<null> {
    if (!this.apiKey) {
      void vscode.window.showWarningMessage(
        'Fathom: set fathom.claudeApiKey to enable explanations (Phase 4)',
      );
    }
    return null;
  }
}
