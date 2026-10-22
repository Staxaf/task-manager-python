"""
@file comments.py
@brief REST router for Comment resources.
@ingroup Comments
"""

from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import select

from app.database import SessionDep
from app.deps import require_user_if_set
from app.models import Comment, Task
from app.schemas import CommentRead, UpdateComment

##
# @brief HTTP endpoints under `/comments` for list / get / update / delete.
# @ingroup Comments
#
# @details
# Comment **creation** is handled via `POST /tasks/{id}/comments` on the
# tasks router (keeps the Task → Comment relation explicit).
#
# | Method | Path | Handler |
# |--------|------|---------|
# | GET | /comments | list_comments |
# | GET | /comments/{comment_id} | get_comment |
# | PATCH | /comments/{comment_id} | update_comment |
# | DELETE | /comments/{comment_id} | delete_comment |
#
# @see Comment
# @see Task
router = APIRouter(prefix="/comments", tags=["comments"])


def _get_comment_or_404(session: SessionDep, comment_id: str) -> Comment:
    """Load a comment by id or raise HTTP 404."""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Comment with id "{comment_id}" not found',
        )
    return comment


##
# @brief Lists all comments across all tasks.
# @param session Database session.
# @return Array of comments (HTTP 200).
@router.get("", response_model=list[CommentRead])
def list_comments(session: SessionDep) -> list[Comment]:
    """Retrieve all comments."""
    return list(
        session.exec(select(Comment).order_by(Comment.created_at.desc())).all()
    )


##
# @brief Retrieves a single comment by UUID.
# @param comment_id Comment UUID from the path.
# @param session Database session.
# @return The matching comment (HTTP 200).
# @throws HTTPException When the comment does not exist (HTTP 404).
@router.get("/{comment_id}", response_model=CommentRead)
def get_comment(comment_id: str, session: SessionDep) -> Comment:
    """Retrieve a comment by ID."""
    return _get_comment_or_404(session, comment_id)


##
# @brief Partially updates a comment.
# @param comment_id Comment UUID from the path.
# @param body Fields to update.
# @param session Database session.
# @return The updated comment (HTTP 200).
# @throws HTTPException When the comment or target task does not exist (HTTP 404).
@router.patch("/{comment_id}", response_model=CommentRead)
def update_comment(
    comment_id: str, body: UpdateComment, session: SessionDep
) -> Comment:
    """Update a comment."""
    comment = _get_comment_or_404(session, comment_id)
    data = body.model_dump(exclude_unset=True)

    if "task_id" in data:
        task = session.get(Task, data["task_id"])
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task with id "{data["task_id"]}" not found',
            )
    if "author_id" in data:
        require_user_if_set(session, data["author_id"], label="Author")

    for key, value in data.items():
        setattr(comment, key, value)

    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


##
# @brief Deletes a comment by UUID.
# @param comment_id Comment UUID from the path.
# @param session Database session.
# @throws HTTPException When the comment does not exist (HTTP 404).
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: str, session: SessionDep) -> Response:
    """Delete a comment."""
    comment = _get_comment_or_404(session, comment_id)
    session.delete(comment)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
