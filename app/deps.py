"""
@file deps.py
@brief Shared request helpers for looking up related entities.
@ingroup Application
"""

from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models import User


##
# @brief Ensures a user id is either omitted or refers to an existing @ref User.
# @param session Database session.
# @param user_id Optional user UUID.
# @param label Human-readable role used in the 404 message (`owner`, `assignee`, …).
# @throws HTTPException When the user id is set but no matching user exists.
def require_user_if_set(
    session: Session, user_id: Optional[str], label: str = "User"
) -> None:
    """Raise 404 when a non-null user_id does not exist."""
    if user_id is None:
        return
    if not session.get(User, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{label} with id "{user_id}" not found',
        )
