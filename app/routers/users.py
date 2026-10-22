"""
@file users.py
@brief REST router for User resources.
@ingroup Users
"""

from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import select

from app.database import SessionDep
from app.models import Comment, Project, Task, User
from app.schemas import (
    CommentRead,
    CreateUser,
    ProjectRead,
    TaskRead,
    UpdateUser,
    UserRead,
)

##
# @brief HTTP endpoints under `/users` for User CRUD and related listings.
# @ingroup Users
#
# @details
# | Method | Path | Handler |
# |--------|------|---------|
# | POST | /users | create_user |
# | GET | /users | list_users |
# | GET | /users/{user_id}/projects | list_user_projects |
# | GET | /users/{user_id}/tasks | list_user_tasks |
# | GET | /users/{user_id}/comments | list_user_comments |
# | GET | /users/{user_id} | get_user |
# | PATCH | /users/{user_id} | update_user |
# | DELETE | /users/{user_id} | delete_user |
#
# @see User
# @see Project
# @see Task
# @see Comment
router = APIRouter(prefix="/users", tags=["users"])


def _get_user_or_404(session: SessionDep, user_id: str) -> User:
    """Load a user by id or raise HTTP 404."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id "{user_id}" not found',
        )
    return user


##
# @brief Creates a new user.
# @param body Validated request body.
# @param session Database session.
# @return The created user (HTTP 201).
@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(body: CreateUser, session: SessionDep) -> User:
    """Create a user."""
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'User with email "{body.email}" already exists',
        )
    user = User(name=body.name, email=body.email)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


##
# @brief Lists all users.
# @param session Database session.
# @return Array of users (HTTP 200).
@router.get("", response_model=list[UserRead])
def list_users(session: SessionDep) -> list[User]:
    """Retrieve all users."""
    return list(session.exec(select(User).order_by(User.created_at.desc())).all())


##
# @brief Lists projects owned by a user.
# @param user_id User UUID from the path.
# @param session Database session.
# @return Array of projects (HTTP 200).
@router.get("/{user_id}/projects", response_model=list[ProjectRead])
def list_user_projects(user_id: str, session: SessionDep) -> list[Project]:
    """Retrieve projects owned by a user."""
    _get_user_or_404(session, user_id)
    return list(
        session.exec(
            select(Project)
            .where(Project.owner_id == user_id)
            .order_by(Project.created_at.desc())
        ).all()
    )


##
# @brief Lists tasks assigned to a user.
# @param user_id User UUID from the path.
# @param session Database session.
# @return Array of tasks (HTTP 200).
@router.get("/{user_id}/tasks", response_model=list[TaskRead])
def list_user_tasks(user_id: str, session: SessionDep) -> list[Task]:
    """Retrieve tasks assigned to a user."""
    _get_user_or_404(session, user_id)
    return list(
        session.exec(
            select(Task)
            .where(Task.assignee_id == user_id)
            .order_by(Task.created_at.desc())
        ).all()
    )


##
# @brief Lists comments authored by a user.
# @param user_id User UUID from the path.
# @param session Database session.
# @return Array of comments (HTTP 200).
@router.get("/{user_id}/comments", response_model=list[CommentRead])
def list_user_comments(user_id: str, session: SessionDep) -> list[Comment]:
    """Retrieve comments authored by a user."""
    _get_user_or_404(session, user_id)
    return list(
        session.exec(
            select(Comment)
            .where(Comment.author_id == user_id)
            .order_by(Comment.created_at.desc())
        ).all()
    )


##
# @brief Retrieves a single user by UUID.
# @param user_id User UUID from the path.
# @param session Database session.
# @return The matching user (HTTP 200).
@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: str, session: SessionDep) -> User:
    """Retrieve a user by ID."""
    return _get_user_or_404(session, user_id)


##
# @brief Partially updates a user.
# @param user_id User UUID from the path.
# @param body Fields to update.
# @param session Database session.
# @return The updated user (HTTP 200).
@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: str, body: UpdateUser, session: SessionDep) -> User:
    """Update a user."""
    user = _get_user_or_404(session, user_id)
    data = body.model_dump(exclude_unset=True)
    if "email" in data:
        clash = session.exec(
            select(User).where(User.email == data["email"], User.id != user_id)
        ).first()
        if clash:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'User with email "{data["email"]}" already exists',
            )
    for key, value in data.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


##
# @brief Deletes a user; related FKs are set to null (not cascaded).
# @param user_id User UUID from the path.
# @param session Database session.
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, session: SessionDep) -> Response:
    """Delete a user."""
    user = _get_user_or_404(session, user_id)
    session.delete(user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
