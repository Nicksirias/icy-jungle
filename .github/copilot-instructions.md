# Copilot Instructions for AI Coding Agents

## Project Overview
This is a Django-based web application for event and group management, with user profiles, group/venue/event creation, and RSVP functionality. The architecture is modular, with core logic in the `core/` app and project configuration in `webapp/`. SQL files in `supabase_schemas/` and `supabase_trigger_create_user.sql` suggest integration with Supabase for data sync or triggers.

## Key Components
- `core/`: Main Django app. Contains models, views, forms, admin, migrations, and templates for user, group, and event management.
- `webapp/`: Django project settings, ASGI/WSGI entrypoints, and URL routing.
- `supabase_schemas/`: SQL schemas for syncing events, RSVPs, and users with Supabase.
- `Dockerfile`: Containerization for local/dev/prod environments.
- `manage.py`: Standard Django management script.

## Developer Workflows
- **Run locally:**
  ```bash
  python manage.py runserver
  ```
- **Apply migrations:**
  ```bash
  python manage.py migrate
  ```
- **Run tests:**
  ```bash
  python manage.py test core
  ```
- **Build Docker image:**
  ```bash
  docker build -t icy-jungle .
  ```
- **Supabase integration:**
  - Use SQL files in `supabase_schemas/` to sync tables with Supabase.
  - Triggers in `supabase_trigger_create_user.sql` for user creation events.

## Project-Specific Patterns
- **Templates:** Located in `core/templates/core/`. Use Django template inheritance (`base.html`) and context variables for rendering forms and lists.
- **Models:** Defined in `core/models.py`. Follow Django ORM conventions, but check for custom fields or methods related to events, groups, and RSVPs.
- **Views:** Use class-based or function-based views in `core/views.py`. Patterns may include custom authentication or event filtering.
- **Forms:** Custom forms in `core/forms.py` for user, event, and group creation.
- **Admin:** Custom admin logic in `core/admin.py` for managing models.

## Integration Points
- **Supabase:** Syncs user, event, and RSVP data via SQL schemas and triggers.
- **Docker:** Containerizes the Django app for consistent deployment.

## Conventions & Patterns
- **App structure:** All business logic in `core/`, project config in `webapp/`.
- **Templates:** Use `core/templates/core/` for all HTML views.
- **Testing:** Tests in `core/tests.py`.
- **Migrations:** All migrations in `core/migrations/`.

## Examples
- To add a new event model, update `core/models.py`, create a form in `core/forms.py`, and a template in `core/templates/core/event_form.html`.
- To sync a new table with Supabase, add a SQL schema to `supabase_schemas/` and update triggers as needed.

---

For questions or unclear patterns, review `README.md` and inspect the relevant files in `core/` and `webapp/`.
