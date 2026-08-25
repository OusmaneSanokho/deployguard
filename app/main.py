import os
from datetime import datetime

import psycopg2
from fastapi import FastAPI, HTTPException

app = FastAPI()
@app.on_event("startup")
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS deployments (
                id SERIAL PRIMARY KEY,
                version TEXT NOT NULL,
                deployed_at TIMESTAMP NOT NULL
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Startup DB init skipped: {e}")

APP_VERSION = "0.1.0"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": APP_VERSION}


def get_db_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
    )


@app.post("/deployments")
def create_deployment():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO deployments (version, deployed_at) VALUES (%s, %s)",
            (APP_VERSION, datetime.utcnow()),
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "recorded", "version": APP_VERSION}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")


@app.get("/deployments")
def list_deployments():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version, deployed_at FROM deployments ORDER BY deployed_at DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {"deployments": [{"version": r[0], "deployed_at": r[1].isoformat()} for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")