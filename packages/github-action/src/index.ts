import * as core from '@actions/core';
import * as exec from '@actions/exec';
import * as github from '@actions/github';
import * as path from 'path';
import { upsertComment } from './comment';

async function run(): Promise<void> {
  const analyzePath = core.getInput('path') || 'tests/';
  const pythonVersion = core.getInput('python-version') || '3.11';
  const token = process.env.GITHUB_TOKEN;

  if (!token) {
    core.setFailed('GITHUB_TOKEN is required');
    return;
  }

  const actionDir = __dirname;
  const analyzerPath = path.resolve(actionDir, '../../analyzer');

  core.info(`Installing fathom-analyzer from ${analyzerPath}`);
  await exec.exec('pip', ['install', analyzerPath]);

  core.info(`Running fathom check on ${analyzePath}`);
  const markdown = await exec.getExecOutput('fathom', [
    'check',
    analyzePath,
    '--format',
    'markdown',
    '--no-mascot',
    '--no-save',
    '--no-git',
  ]);

  if (markdown.exitCode !== 0) {
    core.setFailed(`fathom check failed with exit code ${markdown.exitCode}`);
    return;
  }

  if (github.context.eventName === 'pull_request') {
    const octokit = github.getOctokit(token);
    await upsertComment(octokit, github.context, markdown.stdout);
    core.info('Posted Fathom PR comment');
  } else {
    core.info('Not a pull request — skipping comment');
    core.info(markdown.stdout);
  }
}

run().catch((error) => {
  core.setFailed(error instanceof Error ? error.message : String(error));
});
