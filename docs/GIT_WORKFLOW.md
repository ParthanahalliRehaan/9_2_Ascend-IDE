# Git workflow

Never push directly to main. Branch, PR, teammate review, squash-merge.

Setup once:

    git config core.hooksPath scripts/hooks
    gh auth login

Every task:

    git switch main
    git pull
    git switch -c pX/weekN-topic
    git add <specific files>
    git commit -m "feat(scope): what changed"
    git push -u origin pX/weekN-topic
    gh pr create --fill --base main

Then: teammate approves within 4 hours, CI green, squash-merge, delete branch,
git switch main && git pull.

Rules: small PRs, only edit files you own, never commit secrets,
prefixes feat/fix/docs/test/chore, openapi.yaml needs all three approvals.