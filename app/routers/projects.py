"""
@file projects.py
@brief REST router for Project resources and nested tasks.
@ingroup Projects
"""

from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import select

from app.database import SessionDep
from app.deps import require_user_if_set
from app.models import Project, Task
from app.schemas import CreateProject, CreateTask, ProjectRead, TaskRead, UpdateProject

##
# @brief HTTP endpoints under `/projects` for Project CRUD and nested Tasks.
# @ingroup Projects
#
# @details
# | Method | Path | Handler |
# |--------|------|---------|
# | POST | /projects | create_project |
# | GET | /projects | list_projects |
# | GET | /projects/{project_id}/tasks | list_project_tasks |
# | POST | /projects/{project_id}/tasks | create_project_task |
# | GET | /projects/{project_id} | get_project |
# | PATCH | /projects/{project_id} | update_project |
# | DELETE | /projects/{project_id} | delete_project |
#
# @see Project
# @see Task
router = APIRouter(prefix="/projects", tags=["projects"])


def _get_project_or_404(session: SessionDep, project_id: str) -> Project:
    """Load a project by id or raise HTTP 404."""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Project with id "{project_id}" not found',
        )
    return project


##
# @brief Creates a new project.
# @param body Validated request body.
# @param session Database session.
# @return The created project (HTTP 201).
@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(body: CreateProject, session: SessionDep) -> Project:
    """Create a project."""
    require_user_if_set(session, body.owner_id, label="Owner")
    project = Project(
        name=body.name,
        description=body.description,
        status=body.status,
        owner_id=body.owner_id,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


##
# @brief Lists all projects including their tasks.
# @param session Database session.
# @return Array of projects (HTTP 200).
@router.get("", response_model=list[ProjectRead])
def list_projects(session: SessionDep) -> list[Project]:
    """Retrieve all projects."""
    return list(
        session.exec(select(Project).order_by(Project.created_at.desc())).all()
    )


##
# @brief Lists all tasks belonging to a project.
# @param project_id Project UUID from the path.
# @param session Database session.
# @return Array of tasks (HTTP 200).
# @throws HTTPException When the project does not exist (HTTP 404).
@router.get("/{project_id}/tasks", response_model=list[TaskRead])
def list_project_tasks(project_id: str, session: SessionDep) -> list[Task]:
    """Retrieve all tasks belonging to a project."""
    _get_project_or_404(session, project_id)
    return list(
        session.exec(
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
        ).all()
    )


##
# @brief Creates a new task under the given project.
# @param project_id Parent project UUID from the path.
# @param body Validated request body.
# @param session Database session.
# @return The created task (HTTP 201).
# @throws HTTPException When the project does not exist (HTTP 404).
@router.post(
    "/{project_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project_task(
    project_id: str, body: CreateTask, session: SessionDep
) -> Task:
    """Create a task in a project."""
    _get_project_or_404(session, project_id)
    require_user_if_set(session, body.assignee_id, label="Assignee")
    task = Task(
        title=body.title,
        description=body.description,
        status=body.status,
        priority=body.priority,
        project_id=project_id,
        due_date=body.due_date,
        assignee_id=body.assignee_id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


##
# @brief Retrieves a single project by UUID.
# @param project_id Project UUID from the path.
# @param session Database session.
# @return The matching project (HTTP 200).
# @throws HTTPException When the project does not exist (HTTP 404).
@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, session: SessionDep) -> Project:
    """Retrieve a project by ID."""
    return _get_project_or_404(session, project_id)


##
# @brief Partially updates a project.
# @param project_id Project UUID from the path.
# @param body Fields to update.
# @param session Database session.
# @return The updated project (HTTP 200).
# @throws HTTPException When the project does not exist (HTTP 404).
@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: str, body: UpdateProject, session: SessionDep
) -> Project:
    """Update a project."""
    project = _get_project_or_404(session, project_id)
    data = body.model_dump(exclude_unset=True)
    if "owner_id" in data:
        require_user_if_set(session, data["owner_id"], label="Owner")
    for key, value in data.items():
        setattr(project, key, value)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


##
# @brief Deletes a project and all of its associated tasks.
# @param project_id Project UUID from the path.
# @param session Database session.
# @throws HTTPException When the project does not exist (HTTP 404).
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, session: SessionDep) -> Response:
    """Delete a project and its tasks."""
    project = _get_project_or_404(session, project_id)
    session.delete(project)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
