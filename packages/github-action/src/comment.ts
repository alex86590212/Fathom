import type { Context } from '@actions/github/lib/context';

const MARKER = '<!-- fathom-report -->';

export async function upsertComment(
  octokit: ReturnType<typeof import('@actions/github').getOctokit>,
  context: Context,
  body: string,
): Promise<void> {
  if (!context.payload.pull_request) {
    return;
  }

  const { owner, repo } = context.repo;
  const issueNumber = context.payload.pull_request.number;

  const fullBody = body.includes(MARKER) ? body : `${body}\n${MARKER}`;

  const { data: comments } = await octokit.rest.issues.listComments({
    owner,
    repo,
    issue_number: issueNumber,
  });

  const existing = comments.find(
    (c) => c.user?.type === 'Bot' && c.body?.includes(MARKER),
  );

  if (existing) {
    await octokit.rest.issues.updateComment({
      owner,
      repo,
      comment_id: existing.id,
      body: fullBody,
    });
    return;
  }

  await octokit.rest.issues.createComment({
    owner,
    repo,
    issue_number: issueNumber,
    body: fullBody,
  });
}
