import { execFile } from 'child_process';
import { existsSync } from 'fs';
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

interface AnalyzerCommand {
  command: string;
  prefixArgs: string[];
}

function resolveAnalyzerCommand(): AnalyzerCommand {
  const config = vscode.workspace.getConfiguration('fathom');
  const analyzerPath = config.get<string>('analyzerPath', '').trim();
  const pythonPath = config.get<string>('pythonPath', 'python3').trim() || 'python3';

  if (analyzerPath) {
    return { command: analyzerPath, prefixArgs: [] };
  }

  return { command: pythonPath, prefixArgs: ['-m', 'fathom'] };
}

async function runFathom(args: string[]): Promise<string> {
  const { command, prefixArgs } = resolveAnalyzerCommand();
  try {
    const { stdout } = await execFileAsync(command, [...prefixArgs, ...args], {
      env: process.env,
      maxBuffer: 10 * 1024 * 1024,
    });
    return stdout;
  } catch (err) {
    const hint = resolveAnalyzerCommand();
    const tried = [hint.command, ...hint.prefixArgs].join(' ');
    throw new Error(
      `${err instanceof Error ? err.message : String(err)} (tried: ${tried}). ` +
        'Set fathom.pythonPath or fathom.analyzerPath in settings. ' +
        'Install CLI: pip install -e packages/analyzer',
    );
  }
}

export async function runCheck(testsPath: string): Promise<FathomReport> {
  const stdout = await runFathom([
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
  const stdout = await runFathom(['score', filePath, '--format', 'json']);
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
    if (existsSync(tests.fsPath)) {
      return tests.fsPath;
    }
  }
  return undefined;
}
