# Student Performance Analysis

This repository contains a Flask API and dashboard at the root for Vercel deployment, plus the full Streamlit interface in `student_performance_analysis/app.py`.

## Deploy to Vercel

From the repository root:

```bash
npm install -g vercel
vercel login
vercel
```

Use `vercel --prod` for a production deployment. Vercel detects the Flask `app` exported by `app.py` automatically.

The deployed API exposes `/health`, `/api/summary`, `/api/performance`, and `/api/demo`.

The SQLite database is included for demo use. Vercel function filesystems are ephemeral, so use a hosted database for persistent production data.
