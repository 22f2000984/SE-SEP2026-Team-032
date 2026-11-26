# Run and host Mentor Connect (backend on Render, database on Supabase, frontend on Vercel)

The frontend has two modes. **Without** `VITE_API_URL` it runs on sample data in the browser.
**With** `VITE_API_URL` it uses the Flask backend for everything.

## 1. Fill in the settings

```bash
cd "Milestone 3/backend"
cp .env.example .env     # skip if .env already exists
```

| Setting | Where to get it | If left empty |
|---|---|---|
| `DATABASE_URL` | Supabase > Connect > Session pooler | local SQLite file |
| `SECRET_KEY` | any long random text | development key (not for a live site) |
| `ADMIN_PASSWORD` | choose one before the first start | `demo123` |
| `OPENAI_API_KEY` | platform.openai.com > API keys | simple rules instead of AI |
| `BREVO_API_KEY`, `EMAIL_FROM` | Brevo > SMTP & API > API keys; a verified sender | emails are only logged |
| `JOBS_SECRET` | any long random text | reminder job is off |

`ADMIN_PASSWORD` is used only when the admin account is first created.
The Supabase tables are created by the app on its first start (an existing database from Sprint 1 also needs `supabase_update.sql`).

## 2. Run on your laptop (two terminals)

```bash
# Terminal 1: backend on http://localhost:5001
cd "Milestone 3/backend"
source venv/bin/activate            # first time: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
python app.py
```

```bash
# Terminal 2: frontend on http://localhost:5173
cd "Milestone 2/frontend"
npm install                          # first time only
VITE_API_URL=http://localhost:5001 npm run dev
```

Demo logins (password `demo123`, when `LOAD_DEMO_DATA=1`): `admin@client.test`, `asha@ds.study.iitm.ac.in` (student), `meera@mentor.test` (mentor).
Students must register with an IITM email; mentors can use any email.

## 3. Backend on Render

1. **New > Blueprint** on https://render.com (it reads `render.yaml`), or keep your existing web service.
2. Under **Environment** add the settings from the table above.
3. Open `https://YOUR-SERVICE.onrender.com/api/health`. It should show `{"status": "ok"}`.
4. Set `CORS_ORIGINS` to your Vercel address.

The free service sleeps after about 15 minutes without requests, so the first request can take a minute.
With `DATABASE_URL` set, the data is kept in Supabase and survives restarts.

## 4. Frontend on Vercel

1. Project root directory `Milestone 2/frontend`; environment variable `VITE_API_URL` = the Render address, no trailing slash.
2. Redeploy (Vite reads the variable at build time).

## 5. Weekly reminder emails

In the GitHub repository: **Settings > Secrets and variables > Actions**, add `BACKEND_URL` (the Render address) and
`JOBS_SECRET` (the same value as on Render). The workflow `.github/workflows/reminders.yml` then calls
`POST /api/jobs/reminders` every day. Run it once by hand from the **Actions** tab to check it.
