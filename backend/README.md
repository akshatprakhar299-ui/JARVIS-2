# Backend

## Setup

On macOS, use `python3` rather than `python` unless you have configured a
`python` alias. From the repository root:

```sh
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Before starting the server, configure both required credentials:

- Set `GROQ_API_KEY` in `backend/.env`.
- Place the Firebase Admin service account JSON at
  `backend/services/firebase-admin.json`.

These credentials are required by the LLM and authentication services. Do not
commit either file.

## Run

From the `backend` directory:

```sh
.venv/bin/python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The health endpoint is available at <http://127.0.0.1:8000/health>.
