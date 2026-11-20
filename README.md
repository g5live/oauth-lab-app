# OAuth Lab App

A small learning project that uses Google sign-in to manage a network lab inventory. Each signed-in user can add, view and delete their own devices.

The FastAPI backend handles login and stores devices in a local SQLite database. The React frontend displays the inventory.

## Set up Google sign-in

Create a Google OAuth web client. Add this authorised redirect URI:

```text
http://localhost:8000/auth/callback
```

If the Google app is in testing mode, add your Google account as a test user. Copy `backend/.env.example` to `backend/.env`, fill in your own client ID and secret, and set a long random `SESSION_SECRET`.

Keep the real `.env` private. The example file contains no credentials.

## Start the backend

From the repository folder, with Python 3.15:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1
```

In PyCharm, the combined project currently uses the root `.venv` interpreter. Install the same backend requirements there if using that interpreter:

```bash
.venv/bin/python -m pip install -r backend/requirements.txt
```

The local **Backend** run configuration runs the `uvicorn` module with `main:app --reload --host 127.0.0.1 --port 8000`, using `backend/` as its working directory. Mark `backend/` as a Sources Root so its local imports resolve. The terminal instructions above use the separate `backend/.venv`; both environments need the declared requirements. Running `main.py` directly defines the app but does not start the server.

## Start the frontend

In a second terminal, from the repository folder, with Node.js 22.12 or newer:

```bash
cd frontend
npm ci
npm run dev
```

Open [http://localhost:5173/](http://localhost:5173/) and choose **Sign in with Google**. Use `localhost` consistently in the browser; switching to `127.0.0.1` changes which cookies are sent.

In WebStorm, open `frontend/`. Both folders belong to the single Git repository above them.

## Limits

This is a local authentication and CRUD lab, not a production service. Session cookies are signed, not encrypted. There is no edit-device screen yet. The workload-permission exercise uses a fixed simulated worker, local allow grants and dummy secrets; it is not a real secrets manager or separately authenticated workload. Credentials, the local database, virtual environments, build output and `node_modules` are excluded from Git.
