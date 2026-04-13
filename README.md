![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)
![Python](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-CSS-38bdf8?logo=tailwindcss&logoColor=white)

# py-flashcards

> Django web app for decks, multiple-choice flashcards, and spaced-repetition reviews.

**py-flashcards** is a learning tool: you organize cards into decks, each card has a question and several answers (exactly one correct), and your progress is tracked with per-user review state and review history. The UI uses Tailwind CSS and Crispy Forms with the Tailwind pack.

**Live site:** [http://flashcards.miroszdevelopment.pl/](http://flashcards.miroszdevelopment.pl/)

## Installing / Getting started

Minimal steps to run the site locally with SQLite (default).

```shell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Register an account or use the admin after `createsuperuser`. Static CSS is already built under `theme/static/css/dist/`; if styles look wrong after a fresh clone, build the theme (see **Developing**).

### Initial configuration

- **Python 3.11+** is recommended (Black target in `pyproject.toml` is 3.11).
- **Node.js** is required if you rebuild frontend assets. Install theme dependencies either with Django Tailwind’s installer or manually:

  ```shell
  python manage.py tailwind install
  ```

  or:

  ```shell
  cd theme/static_src
  npm install
  ```

- **`NPM_BIN_PATH`** in `config/settings.py` points at the `npm` executable. On Windows it may be set to a machine-specific path; change it to your `npm`/`npm.cmd` so Tailwind-related management commands can find npm.

- **Secret key and production**: `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` in `config/settings.py` are development defaults. For any shared or production deployment, use environment variables or a separate settings module and never commit real secrets.

## Developing

Clone the repo, create a virtualenv, install Python dependencies, apply migrations, and run the dev server.

```shell
git clone https://github.com/YOUR_USERNAME/py-flashcards.git
cd py-flashcards
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

On Unix-like systems, activate the venv with `source .venv/bin/activate` instead of `.venv\Scripts\activate`.

Useful parallel workflows:

- **Tailwind watch** (rebuild CSS on change), from `theme/static_src`:

  ```shell
  cd theme/static_src
  npm run dev
  ```

  or, if you use django-tailwind’s dev server integration:

  ```shell
  python manage.py tailwind start
  ```

- **Tests** (pytest-django):

  ```shell
  pytest
  ```

- **Lint / format**: Flake8 config is in `.flake8`; Black settings are in `pyproject.toml` (`line-length = 120`).

The data model is summarized in [`models.mermaid`](models.mermaid) (User, Deck, Flashcard, Answer, FlashcardUserState, Review).

### Building

Production-style Tailwind build (minified CSS into `theme/static/css/dist/`):

```shell
cd theme/static_src
npm run build
```

Or:

```shell
python manage.py tailwind build
```

After code or template changes that affect styling, run a build before deployment so `collectstatic` serves up-to-date CSS.

### Deploying / Publishing

Typical Django deployment (adapt to your host):

1. Set `DEBUG=False`, configure `ALLOWED_HOSTS`, and inject a strong `SECRET_KEY`.
2. Point `DATABASES` at your production database if you move off SQLite.
3. Run migrations: `python manage.py migrate`.
4. Collect static files: `python manage.py collectstatic`.
5. Serve the app with Gunicorn/uWSGI/etc. behind a reverse proxy.

There is no single packaged “deploy” command; follow your platform’s Django checklist.

## Features

- **Decks**: Cards grouped per owner (`decks` app).
- **Flashcards**: Question plus multiple **Answer** rows; validation ensures at least one correct answer (`flashcards.services.FlashcardService`).
- **Study flow**: Review UI and URLs under `/flashcards/…` including per-card review (`FlashcardReviewView`).
- **Spaced repetition data**: `FlashcardUserState` (ease factor, next review date) and `Review` events with quality ratings.
- **Auth**: Registration, login, logout (`users` app); login redirects to the flashcard list.
- **Admin**: Django admin for models at `/admin/`.
- **Dev UX**: Django Debug Toolbar; in `DEBUG`, django-browser-reload for live reload.

## Configuration

Main knobs live in `config/settings.py`:

#### `SECRET_KEY`

Type: `str`  
Default: insecure development key in the repo

Used for signing sessions and CSRF. Override in production via environment or a private settings file.

#### `DEBUG`

Type: `bool`  
Default: `True`

Must be `False` in production. Controls extra error pages and inclusion of browser-reload URLs.

#### `ALLOWED_HOSTS`

Type: `list[str]`  
Default: `[]`

Set hostnames your site is allowed to serve when `DEBUG` is `False`.

#### `DATABASES`

Type: dict  
Default: SQLite at `BASE_DIR / "db.sqlite3"`

Swap for PostgreSQL or another backend for production.

#### `NPM_BIN_PATH`

Type: `str` (path to npm)  
Default: Windows-specific example in settings

Required for django-tailwind/npm integration when management commands invoke npm. Set to your local `npm` executable.

#### `INTERNAL_IPS`

Type: `list[str]`  
Default: includes `127.0.0.1`

Used by Django Debug Toolbar to show the panel for local requests.

Example (conceptual — use your real paths and env names):

```bash
set SECRET_KEY=your-production-secret
set DEBUG=False
python manage.py runserver
```

## Contributing

Contributions are welcome. Fork the repository, use a feature branch, and open a pull request.

- Run **pytest** before submitting.
- Match **Black** (120 columns) and **Flake8** as configured in the repo.
- For larger process or style guides, consider adding a `CONTRIBUTING.md` and linking it here.

## Links

- **Repository:** `https://github.com/YOUR_USERNAME/py-flashcards` (replace with your real GitHub URL)
- **Issue tracker:** same repository’s Issues tab
- **Django docs:** [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- **Related:** entity-relationship overview in [`models.mermaid`](models.mermaid)

For sensitive issues (for example security), prefer a private channel to the maintainers instead of a public issue, if you publish that contact.