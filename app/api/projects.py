from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter()

class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

projects = {}

@router.post("/projects", response_model=Project)
async def create_project(project: Project):
    project.id = str(uuid.uuid4())
    projects[project.id] = project
    return project

@router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects[project_id]

@router.get("/projects", response_model=List[Project])
async def list_projects():
    return list(projects.values())

@router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project: Project):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    project.id = project_id
    projects[project_id] = project
    return project

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    del projects[project_id]
    return {"message": "Project deleted successfully"}