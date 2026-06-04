# Contributing to Posture Scanner

Welcome to the team! This guide explains how to work on the project without 
stepping on each other's toes. Read it once before writing any code.

---

## How our branches work

```
main          ← PRODUCTION. Protected. Only the lead engineer can merge here.
                Never push here directly — ever.

staging       ← STAGING / integration. This is where all your work lands.
                Deploys automatically to the staging server when a PR is merged.

feature/xyz   ← YOUR personal branch. Create one for each task you're working on.
                Always branch off staging, always PR back into staging.
```

**Simple rule:** You write code on a `feature/` branch → open a PR into `staging` → 
lead or a teammate reviews → it merges → staging deploys.  
When staging is stable, the lead opens a PR from `staging` into `main` for production.

---

## Step-by-step: Working on a feature

**Step 1 — Make sure you're on the latest staging**
```bash
git checkout staging
git pull origin staging
```

**Step 2 — Create your feature branch**
```bash
git checkout -b feature/your-task-name
# Examples: feature/tls-check, feature/dashboard-chart, feature/login-page
```

**Step 3 — Write your code, commit often**
```bash
git add .
git commit -m "Add TLS certificate expiry check"
# Keep commits small and descriptive — one idea per commit
```

**Step 4 — Push your branch**
```bash
git push origin feature/your-task-name
```

**Step 5 — Open a Pull Request on GitHub**
- Base branch: `staging`
- Compare: `feature/your-task-name`
- Write a short description of what you did and why
- GitHub Actions will run the tests automatically — fix any failures before asking for review

**Step 6 — Wait for review, then merge**
Once approved and tests pass, merge the PR. Staging auto-deploys within a minute.

---

## Running tests locally (do this before every PR)

```bash
cd backend
source venv/bin/activate
pytest
```

All tests must pass before opening a PR. The CI will catch failures, 
but it's faster and less embarrassing to catch them yourself first.

---

## Code style

We use **ruff** for linting. Run it before committing:

```bash
cd backend
ruff check .
```

Ruff will tell you exactly what to fix. Most issues are auto-fixable with:
```bash
ruff check . --fix
```

---

## Commit message format

```
<short description of what changed> (50 chars max)

Optional longer explanation if needed.
```

Good: `Add Secure flag check to cookie engine`  
Bad:  `fix stuff`, `WIP`, `asdfgh`

---

## ❌ Things that will break the project

- Pushing directly to `main` — blocked by branch protection
- Pushing directly to `staging` — please don't, use a PR
- Committing `.env` files — they're in `.gitignore` for a reason; they contain secrets
- Merging a PR with failing tests — the CI gate exists for everyone's protection

---

## Need help?

Open a GitHub Issue or message the lead engineer directly.
