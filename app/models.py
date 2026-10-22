"""
@file models.py
@brief SQLModel table entities for User, Project, Task, and Comment.
@ingroup Domain
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.enums import ProjectStatus, TaskPriority, TaskStatus


def _utcnow() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc)


##
# @brief Person who can own projects, be assigned tasks, and author comments.
# @ingroup Domain
#
# @details
# A User participates in three optional associations:
#
# | Relation | Multiplicity | FK on child | On user delete |
# |----------|--------------|-------------|----------------|
# | User → Project | 1 → * | `owner_id` | `SET NULL` |
# | User → Task | 1 → * | `assignee_id` | `SET NULL` |
# | User → Comment | 1 → * | `author_id` | `SET NULL` |
#
# Deleting a User does **not** delete projects/tasks/comments; FKs become null.
#
# @see Project
# @see Task
# @see Comment
# @see domain_model
#
# @par Persistence
# Mapped to table `users`. Primary key `id` is a generated UUID string.
class User(SQLModel, table=True):
    """User entity referenced by projects, tasks, and comments."""

    __tablename__ = "users"

    ## @brief Unique identifier generated as a UUID.
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    ## @brief Display name (required).
    name: str = Field(max_length=255)

    ## @brief Unique email address (required).
    email: str = Field(max_length=255, unique=True, index=True)

    ## @brief Timestamp when the user row was created.
    created_at: datetime = Field(default_factory=_utcnow)

    ## @brief Projects owned by this user.
    # @see Project
    owned_projects: list["Project"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"foreign_keys": "Project.owner_id"},
    )

    ## @brief Tasks assigned to this user.
    # @see Task
    assigned_tasks: list["Task"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "Task.assignee_id"},
    )

    ## @brief Comments authored by this user.
    # @see Comment
    authored_comments: list["Comment"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={"foreign_keys": "Comment.author_id"},
    )


##
# @brief Aggregate root that groups related Task instances.
# @ingroup Domain
#
# @details
# A Project is the parent side of a **one-to-many** association with @ref Task,
# and optionally references an owning @ref User via `owner_id`.
#
# Deleting a Project deletes every associated Task (and their Comments).
#
# @see Task
# @see User
# @see ProjectStatus
# @see domain_model
#
# @par Persistence
# Mapped to table `projects`. Primary key `id` is a generated UUID string.
class Project(SQLModel, table=True):
    """Project entity that owns many tasks."""

    __tablename__ = "projects"

    ## @brief Unique identifier generated as a UUID.
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    ## @brief Human-readable project name (required).
    name: str = Field(max_length=255)

    ## @brief Longer description of goals or scope.
    description: str = Field(default="")

    ## @brief Current lifecycle status of the project.
    # @see ProjectStatus
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)

    ## @brief Optional foreign key to the owning @ref User.
    # @see User
    owner_id: Optional[str] = Field(
        default=None, foreign_key="users.id", ondelete="SET NULL", index=True
    )

    ## @brief Timestamp when the project row was created.
    created_at: datetime = Field(default_factory=_utcnow)

    ## @brief Owning User entity (navigation property).
    # @see User
    owner: Optional[User] = Relationship(
        back_populates="owned_projects",
        sa_relationship_kwargs={"foreign_keys": "Project.owner_id"},
    )

    ## @brief Collection of tasks that belong to this project.
    # @see Task
    tasks: list["Task"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


##
# @brief Individual work item belonging to exactly one Project.
# @ingroup Domain
#
# @details
# A Task belongs to one @ref Project, may be assigned to one @ref User, and
# owns many @ref Comment instances.
#
# @see Project
# @see Comment
# @see User
# @see TaskStatus
# @see TaskPriority
# @see domain_model
#
# @par Persistence
# Mapped to table `tasks`. Primary key `id` is a generated UUID string.
class Task(SQLModel, table=True):
    """Task entity belonging to one project."""

    __tablename__ = "tasks"

    ## @brief Unique identifier generated as a UUID.
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    ## @brief Short title describing the task (required).
    title: str = Field(max_length=255)

    ## @brief Optional longer description of the work to be done.
    description: str = Field(default="")

    ## @brief Current workflow status of the task.
    # @see TaskStatus
    status: TaskStatus = Field(default=TaskStatus.TODO)

    ## @brief Relative priority of the task within its project.
    # @see TaskPriority
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)

    ## @brief Foreign key referencing the parent Project's `id`.
    # @see Project
    project_id: str = Field(foreign_key="projects.id", ondelete="CASCADE", index=True)

    ## @brief Optional foreign key to the assigned @ref User.
    # @see User
    assignee_id: Optional[str] = Field(
        default=None, foreign_key="users.id", ondelete="SET NULL", index=True
    )

    ## @brief Timestamp when the task row was created.
    created_at: datetime = Field(default_factory=_utcnow)

    ## @brief Optional due date, or `None` if unset.
    due_date: Optional[datetime] = Field(default=None)

    ## @brief Parent Project entity (navigation property).
    # @see Project
    project: Optional[Project] = Relationship(back_populates="tasks")

    ## @brief Assigned User entity (navigation property).
    # @see User
    assignee: Optional[User] = Relationship(
        back_populates="assigned_tasks",
        sa_relationship_kwargs={"foreign_keys": "Task.assignee_id"},
    )

    ## @brief Collection of comments that belong to this task.
    # @see Comment
    comments: list["Comment"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


##
# @brief Text note belonging to exactly one Task.
# @ingroup Domain
#
# @details
# A Comment belongs to one @ref Task and may reference an authoring @ref User
# via `author_id`.
#
# @see Task
# @see User
# @see domain_model
#
# @par Persistence
# Mapped to table `comments`. Primary key `id` is a generated UUID string.
class Comment(SQLModel, table=True):
    """Comment entity belonging to one task."""

    __tablename__ = "comments"

    ## @brief Unique identifier generated as a UUID.
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    ## @brief Comment text body (required).
    body: str = Field(min_length=1)

    ## @brief Optional foreign key to the authoring @ref User.
    # @see User
    author_id: Optional[str] = Field(
        default=None, foreign_key="users.id", ondelete="SET NULL", index=True
    )

    ## @brief Foreign key referencing the parent Task's `id`.
    # @see Task
    task_id: str = Field(foreign_key="tasks.id", ondelete="CASCADE", index=True)

    ## @brief Timestamp when the comment row was created.
    created_at: datetime = Field(default_factory=_utcnow)

    ## @brief Parent Task entity (navigation property).
    # @see Task
    task: Optional[Task] = Relationship(back_populates="comments")

    ## @brief Authoring User entity (navigation property).
    # @see User
    author: Optional[User] = Relationship(
        back_populates="authored_comments",
        sa_relationship_kwargs={"foreign_keys": "Comment.author_id"},
    )
