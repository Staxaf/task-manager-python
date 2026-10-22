"""
@file main.py
@brief Application entry point: boots FastAPI with SQLite and OpenAPI docs.
@ingroup Application
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import comments, projects, tasks, users


##
# @brief Application lifespan: create SQLite tables on startup.
# @ingroup Application
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create database tables when the server starts."""
    create_db_and_tables()
    yield


##
# @brief FastAPI application instance.
# @ingroup Application
#
# @details
# - Persists data in SQLite (`DB_PATH`, default `task-manager.sqlite`).
# - Serves OpenAPI UI at `/api/docs` and ReDoc at `/api/redoc`.
# - Mounts user, project, task, and comment routers.
#
# @see create_db_and_tables
app = FastAPI(
    title="Task Management API",
    description=(
        "REST API for managing users, projects, tasks, and comments. "
        "A Project owns many Tasks; a Task owns many Comments. "
        "Users optionally own projects, are assigned tasks, and author comments. "
        "Deletes cascade Project → Task → Comment; user FKs are set null."
    ),
    version="1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(comments.router)
