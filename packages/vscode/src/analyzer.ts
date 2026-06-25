import { execFile } from 'child_process';
import { promisify } from 'util';
import * as vscode from 'vscode';

const execFileAsync = promisify(execFile);

export type RiskZone = 'critical' | 'fragile' | 'blind_spot' | 'healthy';

export interface FileReport {
  path: string;
  test_honesty_score: number;
  comprehension_score: number;
  risk_zone: RiskZone;
  origin: string;
  findings: Array<{
    file: string;
    line: number;
    pattern: string;
    message: string;
  }>;
}

export interface FathomReport {
  path: string;
  files_scanned: number;
  files: FileReport[];
  summary: Record<RiskZone, number>;
  findings: FileReport['findings'];
}

export interface ScoreResult {
  path: string;
  comprehension_score: number;
  origin: string;
}

function analyzerPath(): string {
  return vscode.workspace.getConfiguration('fathom').get<string>('analyzerPath', 'fathom');
}

export async function runCheck(testsPath: string): Promise<FathomReport> {
  const { stdout } = await execFileAsync(analyzerPath(), [
    'check',
    testsPath,
    '--format',
    'json',
    '--no-mascot',
    '--no-save',
  ]);
  return JSON.parse(stdout) as FathomReport;
}

export async function runScore(filePath: string): Promise<ScoreResult> {
  const { stdout } = await execFileAsync(analyzerPath(), [
    'score',
    filePath,
    '--format',
    'json',
  ]);
  return JSON.parse(stdout) as ScoreResult;
}

export function isTestFile(filePath: string): boolean {
  const name = filePath.split(/[/\\]/).pop() ?? '';
  return name.startsWith('test_') || name.endsWith('_test.py');
}

export function findTestsRoot(): string | undefined {
  const folders = vscode.workspace.workspaceFolders;
  if (!folders?.length) {
    return undefined;
  }
  for (const folder of folders) {
    const tests = vscode.Uri.joinPath(folder.uri, 'tests');
    return tests.fsPath;
  }
  return undefined;
}
