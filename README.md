# Posture Scanner

A security posture scanning SaaS. Users add a domain they own, verify ownership, 
then run a scan that grades the domain's externally-observable security across 
four categories: TLS/SSL, HTTP headers, cookie flags, and open redirects.

**Live scan results are stored per domain**, so teams can chart security improvement over time.

---

## Tech stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Django 5 + Django REST Framework  |
| Auth       | JWT (djangorestframework-simplejwt) |
| Database   | PostgreSQL (managed by Render)    |
| Task queue | Celery + Redis                    |
| Frontend   | React 18 + Vite + Tailwind CSS    |
| Charts     | Recharts                          |
| CI/CD      | GitHub Actions                    |
| Hosting    | Render (API + DB + Redis + worker) |
| Frontend   | Vercel                            |
| Monitoring | Sentry                            |

---

## 🔑 Lead Engineer: First-time GitHub setup

Do these steps **once**, right after creating the repo.

### 1. Create the repo branches

```bash
git clone https://github.com/YOUR_USERNAME/posture-scanner
cd posture-scanner
git checkout -b staging
git push origin staging
git checkout main
```

### 2. Protect the `main` branch

Go to **GitHub → your repo → Settings → Branches → Add branch ruleset** (or "Add rule"):

| Setting | Value |
|---|---|
| Branch name pattern | `main` |
| Require a pull request before merging | ✅ Enabled |
| Required approvals | 1 |
| Require status checks to pass | ✅ Enabled → select the **"Backend tests"** and **"Frontend build"** jobs |
| Require branches to be up to date | ✅ Enabled |
| Restrict who can push to matching branches | ✅ Enabled → add **only yourself** |
| Do not allow bypassing the above settings | ✅ Enabled |

### 3. Protect the `staging` branch

Add another rule for `staging`:

| Setting | Value |
|---|---|
| Branch name pattern | `staging` |
| Require status checks to pass | ✅ Enabled → select the **"Backend tests"** and **"Frontend build"** jobs |

Collaborators can push feature branches and open PRs to `staging` freely, 
but the CI tests must pass before merging.

### 4. Add collaborators

**Settings → Collaborators and Teams → Add people**

Add each team member with **"Write"** access. Write access lets them push 
feature branches and open pull requests, but `main` is still protected by the rules above.

### 5. Add GitHub secrets

**Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Where to get it |
|---|---|
| `RENDER_PROD_DEPLOY_HOOK` | Render → your prod web service → Settings → Deploy hook |
| `RENDER_STAGING_DEPLOY_HOOK` | Render → your staging web service → Settings → Deploy hook |
| `SENTRY_AUTH_TOKEN` | Sentry → Settings → Auth Tokens |
| `SENTRY_ORG` | Your Sentry organisation slug |
| `SENTRY_PROJECT` | Your Sentry project slug |

---

## 🖥️ Local development setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy the example env file and fill in your values
cp .env.example .env

# Apply migrations and start the server
python manage.py migrate
python manage.py createsuperuser  # optional
python manage.py runserver
```

In a second terminal (for async scan tasks):
```bash
cd backend
source venv/bin/activate
celery -A scanner worker --loglevel=info
```

> **Tip:** In dev mode (`scanner.settings.dev`), `CELERY_TASK_ALWAYS_EAGER = True` 
> so tasks run synchronously — you don't need a running worker to trigger scans during development.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env     # set VITE_API_BASE_URL=http://localhost:8000
npm run dev              # http://localhost:5173
```

### Run tests

```bash
cd backend
pytest
```

---

## 🌿 Branching model

```
main ──────────────────────────── PRODUCTION (lead only)
  ↑  (PR, reviewed and merged by lead)
staging ────────────────────────── STAGING (auto-deploys)
  ↑  (PRs from team members)
feature/your-task ──────────────── Your personal work
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full step-by-step workflow.

---

## Deployment

Push to `staging` → GitHub Actions runs tests → deploys to Render staging automatically.  
Open a PR `staging → main` → lead approves → merges → deploys to Render production + creates Sentry release.

Frontend (Vercel) deploys automatically on every push. The `main` branch maps to production; 
all other branches (including `staging`) get preview URLs.

---

## API docs

Once the backend is running, visit:  
`http://localhost:8000/api/schema/swagger-ui/`
