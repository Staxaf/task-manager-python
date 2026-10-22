"""
@file enums.py
@brief Domain enumerations for project and task lifecycle values.
@ingroup Domain
"""

from enum import Enum


##
# @brief Possible lifecycle states of a @ref Project.
# @ingroup Domain
#
# @details
# | Value | Meaning |
# |-------|---------|
# | ACTIVE | Project is ongoing and accepting work (default on create) |
# | COMPLETED | Project work has finished |
# | ARCHIVED | Project is retained for history and no longer active |
#
# @see Project
class ProjectStatus(str, Enum):
    """Lifecycle status values for a Project."""

    ACTIVE = "ACTIVE"  #: Project is ongoing and accepting work.
    COMPLETED = "COMPLETED"  #: Project work has finished.
    ARCHIVED = "ARCHIVED"  #: Project is retained for history.


##
# @brief Possible workflow states of a @ref Task.
# @ingroup Domain
#
# @details
# | Value | Meaning |
# |-------|---------|
# | TODO | Created but work has not started (default on create) |
# | IN_PROGRESS | Currently being worked on |
# | DONE | Completed |
#
# @see Task
class TaskStatus(str, Enum):
    """Workflow status values for a Task."""

    TODO = "TODO"  #: Task has been created but work has not started.
    IN_PROGRESS = "IN_PROGRESS"  #: Task is currently being worked on.
    DONE = "DONE"  #: Task has been completed.


##
# @brief Relative importance of a @ref Task within its @ref Project.
# @ingroup Domain
#
# @details
# | Value | Meaning |
# |-------|---------|
# | LOW | Can be deferred without significant impact |
# | MEDIUM | Normal priority (default on create) |
# | HIGH | Should be addressed sooner than other tasks |
#
# @see Task
class TaskPriority(str, Enum):
    """Priority levels for a Task."""

    LOW = "LOW"  #: Can be deferred without significant impact.
    MEDIUM = "MEDIUM"  #: Normal priority (default).
    HIGH = "HIGH"  #: Should be addressed sooner than other tasks.
