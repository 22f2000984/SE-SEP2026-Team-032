# Run and host the whole app (backend on Render, frontend on Vercel)

The frontend has two modes. **Without** `VITE_API_URL` it runs on sample data in the browser (the Milestone 2 prototype).
**With** `VITE_API_URL` it uses the Flask backend for everything that Sprint 1 built: registration, login, profiles,
availability, admin overview and lists, mentor verification, recommendations and proposing a match, plus accepting,
declining, confirming and cancelling a match. Check-ins, Pulse, feedback and concerns are browser-only previews
until their APIs exist (Sprint 2), so they are hidden in backend mode.

## 1. On your laptop (two terminals)

```bash
# Terminal 1: backend on http://localhost:5001, with sample students, mentors and one proposed match
cd "Milestone 3/backend"
source venv/bin/activate            # first time: python3 -m venv venv && pip install -r requirements.txt
LOAD_DEMO_DATA=1 python app.py

# Terminal 2: frontend on http://localhost:5173, connected to the backend
cd "Milestone 2/frontend"
npm install                          # first time only
VITE_API_URL=http://localhost:5001 npm run dev
```

If you ran an older version of the backend, delete `Milestone 3/backend/instance/mentor_connect.db` first (the match table has new columns) and start again.

Demo logins (password `demo123`): `admin@client.test`, `asha@ds.study.iitm.ac.in` (student), `meera@mentor.test` (mentor).
Students must register with an IITM email; mentors can use any email.

## 2. Backend on Render

1. Push the repo to GitHub. On https://render.com choose **New > Blueprint**, pick the repo; it reads `render.yaml` at the repo root.
   (Or **New > Web Service** with root directory `Milestone 3/backend`, build `pip install -r requirements.txt`,
   start `gunicorn --workers 1 --bind 0.0.0.0:$PORT "app:create_app()"`.)
2. Environment variables (already in `render.yaml`): `SECRET_KEY` (generated), `LOAD_DEMO_DATA=1`, `CORS_ORIGINS`.
3. After the first deploy open `https://YOUR-SERVICE.onrender.com/api/health`. It should show `{"status": "ok"}`.
4. When the Vercel address exists, set `CORS_ORIGINS` to it (for example `https://your-app.vercel.app`) so only your frontend may call the API.

Free plan limits: the service sleeps after about 15 minutes without requests (the first request then takes up to a minute)
and the SQLite file is wiped when it restarts. That is why `LOAD_DEMO_DATA=1` refills the sample data on each start.
Do not put real student data on it.

## 3. Frontend on Vercel

1. In the Vercel project settings (root directory `Milestone 2/frontend`) add the environment variable
   `VITE_API_URL` = the Render address, with no trailing slash (for example `https://YOUR-SERVICE.onrender.com`).
2. Redeploy. Vite reads the variable when it builds, so a change needs a new build.
3. Open the Vercel address and log in with a demo account.

## 4. Optional: stop the free backend from sleeping

A GitHub Action that calls `/api/health` every 10 minutes keeps it awake (GitHub may delay or skip runs, and it
stops after 60 days without commits). It does not stop the data reset on a restart.
