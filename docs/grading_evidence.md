# MDS Grading Evidence

This file maps the MDS laboratory grading rubric to concrete repository evidence.

## A. Implementation

| Requirement | Evidence |
| --- | --- |
| Live demo for the implemented app | Run locally with `docker compose up --build`, then open `http://localhost:3000`. |
| Minimum 2 AI agents as product functionality | Debate agents: Bull, Bear and Judge in `backend/conversations/debate_service.py`; Strategy agent in `backend/strategies/ai_service.py`. |
| Offline demo saved before presentation | Pending: add the YouTube/screencast link here before final submission. |
| Original project topic | AI-assisted stock analysis, portfolio tracking, strategy generation and backtesting. |

## B. AI-Assisted Software Development Process

| Requirement | Evidence |
| --- | --- |
| User stories, minimum 10, and backlog | Tracked in Linear. Pending: export or add Linear project link here. |
| Diagrams | `docs/diagrams.md` contains architecture, AI debate, strategy/backtest and CI workflows. |
| Source control with Git, branches, PRs, minimum 5 commits/student | Current work branch: `feature/portfolio-workflow-hardening`. Author `Stefan <chiperstefan7@gmail.com>` has at least 5 commits in history and this branch adds more. The branch includes a rebase step and a no-fast-forward merge commit for source-control evidence. Create the PR from this branch after pushing. |
| Automated tests, including agent evals | Backend tests under `backend/*/tests.py`; agent evals in `backend/conversations/tests.py`; CI runs `python manage.py test accounts market strategies backtests conversations portfolios`. |
| Bug report and resolution through PR | Portfolio bug report: `docs/bug_report_portfolio.md`. Resolution is implemented on branch `feature/portfolio-workflow-hardening`; open PR from this branch. |
| CI/CD pipeline | `.github/workflows/ci.yml` runs backend lint, Django checks, migrations, backend tests/agent evals, TypeScript and ESLint. |
| AI tools usage report | `docs/ai_usage_report.md`. |

## Verification Commands

```bash
docker compose run --rm --no-deps frontend npx tsc --noEmit
docker compose run --rm --no-deps frontend npm run lint
./.venv/bin/python backend/manage.py test accounts market strategies backtests conversations portfolios
```

## Source Control Evidence

- Branch creation: `feature/portfolio-workflow-hardening`.
- Rebase evidence: support branch `docs/source-control-workflow` was rebased onto `feature/portfolio-workflow-hardening` before merge.
- Merge evidence: support branch `docs/source-control-workflow` was merged back with a no-fast-forward merge commit.
- Pull request: create from `feature/portfolio-workflow-hardening` into `main`.
