# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Django + DRF backend for the ASLCV2 archaeological survey mobile app (https://github.com/ggetzie/aslcv2).
Generated from cookiecutter-django. Python 3.11 / Django 4.2. See `README.md` for database setup,
`api.md` for the REST API contract, `update.md` for the Python/Django upgrade runbook.

## Commands

Virtualenv lives outside the repo: `source /usr/local/src/env/aslcv2_be/bin/activate`.

```bash
./manage.py runserver              # defaults to config.settings.local (see manage.py)
./manage.py migrate                # only touches the `default` (django) DB — see routing below
./manage.py collectstatic --settings config.settings.production
./re_aslcv2_be                     # supervisorctl restart of web + celery (deployed hosts only)

pytest                             # uses pytest.ini: --ds=config.settings.test --reuse-db
pytest main/tests.py::HomePageTest::test_anon_user

npm run dev                        # gulp: sass/js build + browser-sync proxy of runserver
npm run build                      # gulp generate-assets
```

Formatting/linting is via pre-commit (black, isort, flake8 with `setup.cfg`, max-line-length 120).

### Testing reality

`pytest` only collects `main/tests.py` and the `aslcv2_be/users` tests. The bulk of the API coverage
lives in `main/test_local.py` and `main/test_path.py`, which are **not** pytest tests — they are
integration scripts that hit a *running* server over HTTP:

```bash
./manage.py runserver              # in one shell
./manage.py shell                  # in another
>>> from main.test_local import *
>>> test_all()
```

They import `main/test_helpers.py::TestClient`, which authenticates against
`http://127.0.0.1:8000/asl/auth-token/` using `TEST_USERNAME` / `TEST_USER_PW` from `.env`, and read
sample images from `TEST_PHOTOS_DIR`. `test_local.py` refuses to import unless `settings.DEBUG` is on.
The reason for this arrangement (noted in the module docstring): Django's test runner does not handle
the multi-database/multi-schema setup, so these tests run against real local data.

## Architecture

### Two databases, split by model

`config/settings/base.py` defines `default` (Django's own DB, schemas `django,public`) and
`archaeology` (schemas `spatial,options,object`). `config/routers.py` routes by model name: the
`unmanaged` list — `spatialarea`, `areatype`, `spatialcontext`, `contexttype`, `objectfind`,
`materialcategory` — goes to `archaeology`, everything else to `default`.

Those six models are `managed = False` with explicit `db_table` (`areas`, `contexts`, `finds`, …).
**The archaeology schema is owned by other applications, not by Django.** Never write a migration for
them; schema changes go in `main/sql/*.sql` and are applied by hand. Adding a model that belongs in the
archaeology DB means adding its lowercased model name to `unmanaged` in `config/routers.py` too.

Because they live in a different DB, cross-DB ForeignKeys are impossible. The models instead relate
through the coordinate tuple, exposed as manual `@property` accessors that mimic Django's related
managers: `SpatialArea.spatialcontext_set`, `SpatialContext.contextphoto_set` / `bagphoto_set`,
`ObjectFind.spatial_context` / `findphoto_set()`, etc. (see `main/models.py`).

### The HZEN(C)(F) coordinate hierarchy

Everything is keyed by UTM position rather than by surrogate ID:

`utm_hemisphere` (N/S) → `utm_zone` → `area_utm_easting_meters` → `area_utm_northing_meters`
→ `context_number` → `find_number`

This tuple appears three times, and all three must stay in sync when the hierarchy changes:

1. **URLs** — `config/api_router.py` (API) and `main/urls.py` (HTML drill-down views) build paths from
   the tuple. `HemisphereConverter` (regex `[NS]`, registered as `hem`) handles the hemisphere segment.
   Views accept the tuple as URL kwargs *or* as query params (see `FILTER_VARS` in `main/views.py`).
2. **Model helpers** — `hzenc_list()` / `hzenc_dict()` on `SpatialContext`, `hzencf_list()` /
   `hzencf_dict()` on `ObjectFind`. Use these instead of hand-building kwargs.
3. **Media paths** — photos and 3D models live under `MEDIA_ROOT/{H}/{Z}/{E}/{N}/{C}/…`, built by
   `main/models.py::build_findphoto_path` and the `subfolder` properties, and by
   `main/model3d.py::context_subroot`.

`context_number` and `find_number` are auto-incremented per parent in the models' `save()` (max + 1
within the containing area/context). `ObjectFind.save()` also `get_or_create`s the parent area and
context, so a find can be POSTed for coordinates that do not exist yet.

### Photos on disk

Photo files are named by sequential integers within their folder (`1.jpg`, `2.jpg`, …) via
`get_next_photo_number` / `get_photo_filename`. For finds, the filesystem is the source of truth for
listing — `ObjectFind.list_files_photo_folder()` walks the directory rather than querying `FindPhoto`,
so photos dropped in by other tooling still show up. Uploads are `PUT` with a `photo` file part
(`FindPhotoUpload` also accepts `POST`, delegating to `put`). `.jpeg` is normalized to `.jpg`;
`PHOTO_EXTENSIONS` in `main/utils.py` is the accepted set (includes `.cr3`, `.heic`, `.raw`).

`ContextPhoto` / `BagPhoto` thumbnails are generated asynchronously: `main/signals.py` fires on
`post_save`, queueing `main/tasks.py::cp_thumbnail` / `bp_thumbnail` on Celery (broker from
`aslcv2_be_CELERY_BROKER_URL`, redis). `FindPhoto` has no thumbnail.

Every mutating API view writes an `ActionLog` row (user, model verbose name, C/R/U/D, object id).

### URL layout

Everything is mounted under `/asl/`: `/asl/api/…` (DRF, `config/api_router.py`),
`/asl/auth-token/` (DRF token), `/asl/main/…` (server-rendered drill-down browsing in
`main/views.py`), `/asl/admin/`, `/asl/accounts/` (allauth).

DRF defaults (`base.py`): `IsAuthenticated`, Session + Token auth, `LimitOffsetPagination` with
`PAGE_SIZE = 100` — list views that must return everything set `pagination_class = None` explicitly.

### Settings & env

`config/settings/{base,local,test,production}.py`; `base.py` reads `.env` at the repo root
unconditionally via django-environ. Required keys: `DJANGO_DB`, `ARCHAEOLOGY_DB`,
`ARCHAEOLOGY_DB_USER`, `ARCHAEOLOGY_DB_PW`, `aslcv2_be_SECRET_KEY`, `aslcv2_be_CELERY_BROKER_URL`,
plus `TEST_USERNAME` / `TEST_USER_PW` / `TEST_PHOTOS_DIR` for the integration scripts.
`config/celery_app.py` defaults to the *production* settings module.

Note `main/ingest.py` hardcodes `/usr/local/src/aslcv2_be/main/data` — it is a one-off CSV import
helper for the deployed host, not part of the request path.
