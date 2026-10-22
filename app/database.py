"""
@file database.py
@brief SQLite engine, session dependency, and schema bootstrap.
@ingroup Application
"""

import os
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

## Path to the SQLite database file (override with env `DB_PATH`).
DB_PATH = os.getenv("DB_PATH", "task-manager.sqlite")

## SQLAlchemy engine connected to the local SQLite file.
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
    """Enable SQLite foreign keys so ON DELETE CASCADE works."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


##
# @brief Creates all SQLModel tables if they do not exist.
# @ingroup Application
#
# @details Called once at application startup via the FastAPI lifespan hook.
def create_db_and_tables() -> None:
    """Create database tables from SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


##
# @brief Yields a SQLModel session per HTTP request.
# @ingroup Application
#
# @details FastAPI dependency; the session is closed when the request ends.
# @return Generator yielding a @ref Session.
def get_session() -> Generator[Session, None, None]:
    """Provide a database session for a single request."""
    with Session(engine) as session:
        yield session


## Annotated dependency type for injecting a DB session into route handlers.
SessionDep = Annotated[Session, Depends(get_session)]
