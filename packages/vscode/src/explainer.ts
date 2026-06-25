import * as vscode from 'vscode';

export interface ExplanationResult {
  summary: string;
  suggestions: string[];
}

/**
 * On-demand Claude API explanations for red-zone code.
 * Only fires on explicit user hover/action — never in background.
 */
export class Explainer {
  constructor(private readonly apiKey: string) {}

  async explain(filePath: string, line: number): Promise<ExplanationResult | null> {
    if (!this.apiKey) {
      vscode.window.showWarningMessage(
        'Fathom: set fathom.claudeApiKey to enable explanations',
      );
      return null;
    }

    // TODO: call Claude API with file context
    throw new Error('Explainer not yet implemented');
  }
}
