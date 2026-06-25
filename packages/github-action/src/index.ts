/**
 * GitHub Action entry point — comment-only PR risk reports.
 * Hard-fail mode (fail_on: critical) deferred to a later release.
 */

import * as core from '@actions/core';
import * as github from '@actions/github';

async function run(): Promise<void> {
  const path = core.getInput('path') || 'tests/';

  core.info(`Fathom: analyzing ${path}`);
  // Analysis is handled by composite action steps in action.yml
  // This file is a placeholder for future programmatic comment formatting

  if (github.context.eventName !== 'pull_request') {
    core.info('Not a pull request — skipping comment');
    return;
  }

  core.info('Fathom GitHub Action skeleton — comment posting handled in action.yml');
}

run().catch((error) => {
  core.setFailed(error instanceof Error ? error.message : String(error));
});
