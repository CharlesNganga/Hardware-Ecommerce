# Hardware-Ecommerce

Online hardware store for a shop in Nairobi, Kenya. Customers pay by M-Pesa; the shop fulfils orders by pickup or delivery.

Django monolith with server-rendered templates, Tailwind CSS, HTMX and Alpine (added when needed) and PostgreSQL.

## Run it locally

You need Docker with Compose. Nothing else.

```sh
cp .env.example .env
# edit .env: set SECRET_KEY and POSTGRES_PASSWORD
docker compose up
```

Open http://localhost:8000. Three services start: `db` (Postgres), `web` (Django, runs migrations first) and `tailwind` (rebuilds the CSS when templates change). The first start downloads the Tailwind CLI, which takes a moment.

Create a staff login for the admin at http://localhost:8000/admin/:

```sh
docker compose exec web python manage.py createsuperuser
```

## Everyday commands

```sh
docker compose exec web python manage.py test            # tests
docker compose exec web ruff check . && docker compose exec web ruff format --check .   # lint
docker compose exec web python manage.py makemigrations   # after changing models
```

Without Docker (Linux or macOS, Python 3.13, a running Postgres): `pip install -r requirements-dev.txt`, export the variables from `.env.example`, run `sh bin/tailwind build`, then `python manage.py migrate && python manage.py runserver`.

## Layout

| Path | What |
|---|---|
| `config/` | Django settings (all from environment variables), URLs |
| `pages/` | Home page and, later, site settings and contact pages |
| `templates/` | `base.html` and shared `components/` |
| `static_src/css/` | Tailwind source: `tokens.css` (colours, fonts), `base.css`, `components.css` |
| `static/css/app.css` | Built CSS. Not committed |
| `bin/tailwind` | Downloads and runs the pinned Tailwind CLI |

## Configuration

Everything comes from environment variables (see `.env.example`). `SECRET_KEY` is always required. With `DEBUG` off, `ALLOWED_HOSTS` and the `POSTGRES_*` variables are required too, and the app refuses to start without them. Never commit `.env`.

## CI

GitHub Actions runs on every pull request and push to `main`: lint (ruff), CSS build, `makemigrations --check`, tests, and `check --deploy` with production settings.
