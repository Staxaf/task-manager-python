"""
@file schemas.py
@brief Pydantic request/response schemas for the REST API.
@ingroup Application
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.enums import ProjectStatus, TaskPriority, TaskStatus


##
# @brief Request body for `POST /users`.
# @ingroup Users
# @see User
# @see UpdateUser
class CreateUser(BaseModel):
    """Payload for creating a user."""

    ## @brief Display name (required).
    name: str = Field(min_length=1, max_length=255)

    ## @brief Unique email address (required).
    email: EmailStr


##
# @brief Request body for `PATCH /users/{id}`.
# @ingroup Users
# @see User
# @see CreateUser
class UpdateUser(BaseModel):
    """Payload for partially updating a user."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None


##
# @brief Public User representation returned by the API.
# @ingroup Users
class UserRead(BaseModel):
    """User response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    created_at: datetime


##
# @brief Request body for `POST /projects`.
# @ingroup Projects
#
# @details
# Defaults when optional fields are omitted:
# - `description` → `""`
# - `status` → ProjectStatus.ACTIVE
# - `owner_id` → `None`
#
# @see Project
# @see UpdateProject
# @see User
class CreateProject(BaseModel):
    """Payload for creating a project."""

    ## @brief Human-readable project name (required).
    name: str = Field(min_length=1, max_length=255)

    ## @brief Optional project description.
    description: str = ""

    ## @brief Optional initial status.
    # @see ProjectStatus
    status: ProjectStatus = ProjectStatus.ACTIVE

    ## @brief Optional owning user UUID.
    # @see User
    owner_id: Optional[str] = None


##
# @brief Request body for `PATCH /projects/{id}`.
# @ingroup Projects
# @see Project
# @see CreateProject
class UpdateProject(BaseModel):
    """Payload for partially updating a project."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    owner_id: Optional[str] = None


##
# @brief Request body for `POST /projects/{id}/tasks`.
# @ingroup Tasks
#
# @details
# The parent project ID is taken from the URL path, **not** from this body.
#
# @see Task
# @see Project
# @see UpdateTask
# @see User
class CreateTask(BaseModel):
    """Payload for creating a task under a project."""

    ## @brief Short title describing the task (required).
    title: str = Field(min_length=1, max_length=255)

    ## @brief Optional longer description of the work.
    description: str = ""

    ## @brief Optional initial workflow status.
    # @see TaskStatus
    status: TaskStatus = TaskStatus.TODO

    ## @brief Optional priority.
    # @see TaskPriority
    priority: TaskPriority = TaskPriority.MEDIUM

    ## @brief Optional due date (ISO 8601), or null.
    due_date: Optional[datetime] = None

    ## @brief Optional assignee user UUID.
    # @see User
    assignee_id: Optional[str] = None


##
# @brief Request body for `PATCH /tasks/{id}`.
# @ingroup Tasks
# @see Task
# @see CreateTask
class UpdateTask(BaseModel):
    """Payload for partially updating a task."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    project_id: Optional[str] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[str] = None


##
# @brief Request body for `POST /tasks/{id}/comments`.
# @ingroup Comments
#
# @details
# The parent task ID is taken from the URL path, **not** from this body.
#
# @see Comment
# @see Task
# @see UpdateComment
# @see User
class CreateComment(BaseModel):
    """Payload for creating a comment under a task."""

    ## @brief Comment text body (required).
    body: str = Field(min_length=1)

    ## @brief Optional author user UUID.
    # @see User
    author_id: Optional[str] = None


##
# @brief Request body for `PATCH /comments/{id}`.
# @ingroup Comments
# @see Comment
# @see CreateComment
class UpdateComment(BaseModel):
    """Payload for partially updating a comment."""

    body: Optional[str] = Field(default=None, min_length=1)
    author_id: Optional[str] = None
    task_id: Optional[str] = None


##
# @brief Public Comment representation returned by the API.
# @ingroup Comments
class CommentRead(BaseModel):
    """Comment response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    body: str
    author_id: Optional[str] = None
    task_id: str
    created_at: datetime


##
# @brief Public Task representation returned by the API.
# @ingroup Tasks
class TaskRead(BaseModel):
    """Task response model (optionally includes nested comments)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    project_id: str
    assignee_id: Optional[str] = None
    created_at: datetime
    due_date: Optional[datetime] = None
    comments: list[CommentRead] = []


##
# @brief Public Project representation returned by the API.
# @ingroup Projects
class ProjectRead(BaseModel):
    """Project response model (optionally includes nested tasks)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    status: ProjectStatus
    owner_id: Optional[str] = None
    created_at: datetime
    tasks: list[TaskRead] = []
