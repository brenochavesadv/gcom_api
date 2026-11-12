# GCOM Monorepo

Monorepo for the GCOM products:

- [`backend/`](./backend/) — Flask REST API, migrations, backend tests and Python dependencies.
- [`frontend/`](./frontend/) — Flutter workspace entrypoint and client documentation.

## Backend

Run the API from the backend directory so the existing Flask imports and migration commands resolve consistently:

To run commerciall_api in debug mode use:
flask --app backend.apps.commerciall_api.app:create_app --env-file backend/apps/commerciall_api/.env run --debug

```powershell
cd backend
.\.venv\Scripts\Activate.ps1  # if a backend virtual environment is configured
pip install -r requirements.txt
python run.py
```

The API factory remains [`backend/main.py`](./backend/main.py) and the WSGI entrypoint is [`backend/run.py`](./backend/run.py).

## Flutter

The Flutter client belongs under [`frontend/`](./frontend/). Keep Dart packages and Flutter tooling independent from the Python backend. See [`frontend/README.md`](./frontend/README.md) for the expected layout.

## Secrets

Environment files and database credentials are not part of the public monorepo contract. 