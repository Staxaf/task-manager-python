# Task Management REST API

A minimal **Python / FastAPI** REST API for managing **users**, **projects**, **tasks**, and **comments**. Data is persisted locally with **SQLite** (via SQLModel). Interactive API docs are available through OpenAPI/Swagger.

## Domain model

- **User** — `name`, unique `email`; optionally owns projects, is assigned tasks, authors comments.
- **Project** — groups related work (`ACTIVE` | `COMPLETED` | `ARCHIVED`); optional `owner_id`.
- **Task** — belongs to exactly one project; optional `assignee_id`; priority `LOW` | `MEDIUM` | `HIGH`.
- **Comment** — belongs to exactly one task; optional `author_id`.
- Ownership cascade: Project → Task → Comment. Deleting a **User** sets related FKs to `null`.

## Prerequisites

- Python 3.11+
- [Doxygen](https://www.doxygen.nl/) (optional, for HTML docs from comments)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn app.main:app --reload --port 3000
```

The server listens on `http://localhost:3000` (change `--port` as needed).

SQLite database file defaults to `task-manager.sqlite` in the project root (override with `DB_PATH`). Tables are created automatically on startup.

## OpenAPI docs

Open [http://localhost:3000/api/docs](http://localhost:3000/api/docs) for the interactive Swagger UI.

## Endpoints

### Users

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/users` | Create a user |
| `GET` | `/users` | List all users |
| `GET` | `/users/{id}` | Get a user by ID |
| `PATCH` | `/users/{id}` | Update a user |
| `DELETE` | `/users/{id}` | Delete a user (related FKs → null) |
| `GET` | `/users/{id}/projects` | Projects owned by the user |
| `GET` | `/users/{id}/tasks` | Tasks assigned to the user |
| `GET` | `/users/{id}/comments` | Comments authored by the user |

### Projects

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/projects` | Create a project (`owner_id` optional) |
| `GET` | `/projects` | List all projects (includes tasks) |
| `GET` | `/projects/{id}` | Get a project by ID |
| `PATCH` | `/projects/{id}` | Update a project |
| `DELETE` | `/projects/{id}` | Delete a project, its tasks, and their comments |
| `GET` | `/projects/{id}/tasks` | List tasks for a project |
| `POST` | `/projects/{id}/tasks` | Create a task (`assignee_id` optional) |

### Tasks

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/tasks` | List all tasks |
| `GET` | `/tasks/{id}` | Get a task by ID |
| `PATCH` | `/tasks/{id}` | Update a task |
| `DELETE` | `/tasks/{id}` | Delete a task and its comments |
| `GET` | `/tasks/{id}/comments` | List comments for a task |
| `POST` | `/tasks/{id}/comments` | Create a comment (`author_id` optional) |

### Comments

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/comments` | List all comments |
| `GET` | `/comments/{id}` | Get a comment by ID |
| `PATCH` | `/comments/{id}` | Update a comment |
| `DELETE` | `/comments/{id}` | Delete a comment |

### Status codes

- `200` / `201` / `204` — success
- `409 Conflict` — duplicate user email
- `422 Unprocessable Entity` — validation errors
- `404 Not Found` — user, project, task, or comment does not exist

## Example requests

```bash
# Create a user
curl -s -X POST http://localhost:3000/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"Anton","email":"anton@example.com"}'

# Create a project owned by that user (replace USER_ID)
curl -s -X POST http://localhost:3000/projects \
  -H 'Content-Type: application/json' \
  -d '{"name":"Website Redesign","owner_id":"USER_ID"}'

# Create a task assigned to the user (replace PROJECT_ID / USER_ID)
curl -s -X POST http://localhost:3000/projects/PROJECT_ID/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Design homepage mockups","assignee_id":"USER_ID","priority":"HIGH"}'

# Add a comment authored by the user (replace TASK_ID / USER_ID)
curl -s -X POST http://localhost:3000/tasks/TASK_ID/comments \
  -H 'Content-Type: application/json' \
  -d '{"body":"Started Figma drafts","author_id":"USER_ID"}'
```

## Generating Doxygen documentation

Needs `doxygen` and Graphviz (`dot`) on `PATH` (for class / collaboration / call / directory graphs):

```bash
brew install doxygen graphviz   # or any Graphviz install that provides `dot`
doxygen Doxyfile
open docs/html/index.html
```

If Homebrew Graphviz fails to build, a local conda-forge install works too (already used here as `.graphviz/`, gitignored):

```bash
# once: micromamba create -y -p .graphviz -c conda-forge graphviz
PATH="$(pwd)/.graphviz/bin:$PATH" doxygen Doxyfile
```

`Doxyfile` has `HAVE_DOT = YES` (expects `dot` on `PATH`). Source comments use Doxygen tags (`@file`, `@brief`, `@ingroup`, `@see`, …). Overview pages live in `docs/mainpage.dox` and `docs/domain-model.dox`; static SVGs remain under `docs/images/`.

## Project structure

```text
app/
├── main.py              # FastAPI app + lifespan
├── database.py          # SQLite engine / session
├── enums.py             # ProjectStatus, TaskStatus, TaskPriority
├── models.py            # User, Project, Task, Comment entities
├── schemas.py           # Request/response models
├── deps.py              # Shared lookup helpers
└── routers/
    ├── users.py
    ├── projects.py
    ├── tasks.py
    └── comments.py

docs/
Doxyfile
requirements.txt
README.md
```

## License

UNLICENSED (private project).
