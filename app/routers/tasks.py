"""
@file tasks.py
@brief REST router for Task resources and nested comments.
@ingroup Tasks
"""

from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import select

from app.database import SessionDep
from app.deps import require_user_if_set
from app.models import Comment, Project, Task
from app.schemas import CommentRead, CreateComment, TaskRead, UpdateTask

##
# @brief HTTP endpoints under `/tasks` for list / get / update / delete
# and nested Comment create/list.
# @ingroup Tasks
#
# @details
# Task **creation** is handled via `POST /projects/{id}/tasks` on the
# projects router (keeps the Project → Task relation explicit).
#
# | Method | Path | Handler |
# |--------|------|---------|
# | GET | /tasks | list_tasks |
# | GET | /tasks/{task_id}/comments | list_task_comments |
# | POST | /tasks/{task_id}/comments | create_task_comment |
# | GET | /tasks/{task_id} | get_task |
# | PATCH | /tasks/{task_id} | update_task |
# | DELETE | /tasks/{task_id} | delete_task |
#
# @see Task
# @see Comment
# @see Project
router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_task_or_404(session: SessionDep, task_id: str) -> Task:
    """Load a task by id or raise HTTP 404."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Task with id "{task_id}" not found',
        )
    return task


##
# @brief Lists all tasks across all projects.
# @param session Database session.
# @return Array of tasks (HTTP 200).
@router.get("", response_model=list[TaskRead])
def list_tasks(session: SessionDep) -> list[Task]:
    """Retrieve all tasks."""
    return list(session.exec(select(Task).order_by(Task.created_at.desc())).all())


##
# @brief Lists all comments belonging to a task.
# @param task_id Task UUID from the path.
# @param session Database session.
# @return Array of comments (HTTP 200).
# @throws HTTPException When the task does not exist (HTTP 404).
@router.get("/{task_id}/comments", response_model=list[CommentRead])
def list_task_comments(task_id: str, session: SessionDep) -> list[Comment]:
    """Retrieve all comments belonging to a task."""
    _get_task_or_404(session, task_id)
    return list(
        session.exec(
            select(Comment)
            .where(Comment.task_id == task_id)
            .order_by(Comment.created_at.desc())
        ).all()
    )


##
# @brief Creates a new comment under the given task.
# @param task_id Parent task UUID from the path.
# @param body Validated request body.
# @param session Database session.
# @return The created comment (HTTP 201).
# @throws HTTPException When the task does not exist (HTTP 404).
@router.post(
    "/{task_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task_comment(
    task_id: str, body: CreateComment, session: SessionDep
) -> Comment:
    """Create a comment on a task."""
    _get_task_or_404(session, task_id)
    require_user_if_set(session, body.author_id, label="Author")
    comment = Comment(
        body=body.body,
        author_id=body.author_id,
        task_id=task_id,
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


##
# @brief Retrieves a single task by UUID.
# @param task_id Task UUID from the path.
# @param session Database session.
# @return The matching task (HTTP 200).
# @throws HTTPException When the task does not exist (HTTP 404).
@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: str, session: SessionDep) -> Task:
    """Retrieve a task by ID."""
    return _get_task_or_404(session, task_id)


##
# @brief Partially updates a task.
# @param task_id Task UUID from the path.
# @param body Fields to update.
# @param session Database session.
# @return The updated task (HTTP 200).
# @throws HTTPException When the task or target project does not exist (HTTP 404).
@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: str, body: UpdateTask, session: SessionDep) -> Task:
    """Update a task."""
    task = _get_task_or_404(session, task_id)
    data = body.model_dump(exclude_unset=True)

    if "project_id" in data:
        project = session.get(Project, data["project_id"])
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Project with id "{data["project_id"]}" not found',
            )
    if "assignee_id" in data:
        require_user_if_set(session, data["assignee_id"], label="Assignee")

    for key, value in data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


##
# @brief Deletes a task by UUID.
# @param task_id Task UUID from the path.
# @param session Database session.
# @throws HTTPException When the task does not exist (HTTP 404).
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, session: SessionDep) -> Response:
    """Delete a task."""
    task = _get_task_or_404(session, task_id)
    session.delete(task)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
