# GCOM Flask backend

## Flask debug mode

Run the selected application with Flask's debugger and automatic reloader:

```powershell
flask --app backend.apps.commerciall_api.app:create_app `
  --env-file backend/apps/commerciall_api/.env run --debug

flask --app backend.apps.tributos_api.app:create_app `
  --env-file backend/apps/tributos_api/.env run --debug
```

The equivalent environment-variable syntax is:

```powershell
$env:FLASK_APP = "backend.apps.commerciall_api.app:create_app"
$env:FLASK_DEBUG = "1"
flask run
```

Use debug mode only for local development. Do not enable it in production.

Canonical paths: application factories are in `apps/<application_name>/app.py`;
shared configuration is in `backend/config.py`; shared Flask extensions are in
`backend/extensions.py`. Older `main.py` and `core/extensions.py` references
are compatibility-only.

## Application architecture

Each service has its own factory in `apps/<application_name>/app.py` and WSGI
entrypoint in `apps/<application_name>/wsgi.py`. Shared configuration and
extensions live in `backend/extensions.py`. The compatibility `core/extensions.py`
module should not
be used for new deployments.

Start the services with Flask CLI:

```powershell
flask --app backend.apps.commerciall_api.app:create_app --env-file backend/apps/commerciall_api/.env run --debug
flask --app backend.apps.tributos_api.app:create_app --env-file backend/apps/tributos_api/.env run --debug
```

Production WSGI targets:

```text
backend.apps.commerciall_api.wsgi:application
backend.apps.tributos_api.wsgi:application
```

This backend is an application monorepo. Applications live under `apps/`, each exposing `create_app()` from `main.py`. Shared configuration and extensions live under `core/`.

Current applications: `commerciall_api` and `tributos_api`. Future applications should use `apps/<application_name>/main.py` with the same factory contract.

The backend is isolated from the Flutter workspace so Python and Dart dependencies can evolve independently.

- Application factory: [`main.py`](./main.py)
- WSGI entrypoint: [`run.py`](./run.py)
- API modules: [`api_app/`](./api_app/)
- Tests: [`tests/`](./tests/)
- Migrations: [`migrations/`](./migrations/)

Run commands from the repository root:

```powershell
pip install -e .
python -m backend.run

# Flask CLI: commerciall_api
flask --app backend.apps.commerciall_api.app:create_app --env-file backend/apps/commerciall_api/.env run --debug

# Flask CLI: tributos_api
flask --app backend.apps.tributos_api.app:create_app --env-file backend/apps/tributos_api/.env run --debug
pytest
```

Select an application with `FLASK_APP` (`commerciall_api` or `tributos_api`):

```powershell
$env:FLASK_APP = "tributos_api"
python -m backend.run
```

For a single run, use `python -m backend.run --app tributos_api`. WSGI servers
can import `backend.run:application`; set `FLASK_APP` before starting the
server.
