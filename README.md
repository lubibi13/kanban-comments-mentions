# Python FastAPI Starter

A minimal FastAPI + SQLModel + JWT auth starter repo.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Activate on Unix/macOS:

```bash
source .venv/bin/activate
```

Activate on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000. Swagger docs are at http://localhost:8000/docs.

A SQLite DB file will be created automatically at `./app.db`.

## Test

```bash
pytest
```
