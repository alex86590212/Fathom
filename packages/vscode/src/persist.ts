import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import type { FathomReport } from './analyzer';

export function fathomDir(): string {
  const configured = vscode.workspace.getConfiguration('fathom').get<string>('dataDir', '.fathom');
  const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  if (!root) {
    return configured;
  }
  return path.join(root, configured);
}

export function persistReport(report: FathomReport): void {
  const dir = fathomDir();
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'last-check.json'), JSON.stringify(report, null, 2));

  const scores: Record<string, { comprehension: number; honesty: number; zone: string }> = {};
  for (const file of report.files) {
    scores[file.path] = {
      comprehension: file.comprehension_score,
      honesty: file.test_honesty_score,
      zone: file.risk_zone,
    };
  }
  fs.writeFileSync(path.join(dir, 'scores.json'), JSON.stringify(scores, null, 2));
}
