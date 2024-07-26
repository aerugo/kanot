from typing import Any, Callable, Dict

import pytest
from fastapi.testclient import TestClient

from ..models import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    CodeTypeCreate, CodeTypeUpdate, CodeTypeResponse,
    CodeCreate, CodeUpdate, CodeResponse,
    SeriesCreate, SeriesUpdate, SeriesResponse,
    SegmentCreate, SegmentUpdate, SegmentResponse,
    ElementCreate, ElementUpdate, ElementResponse,
    AnnotationCreate, AnnotationUpdate, AnnotationResponse,
    BatchAnnotationCreate, BatchAnnotationRemove
)

@pytest.fixture
def create_project(client: TestClient) -> Callable[[str, str], Dict[str, Any]]:
    def _create_project(title: str = "Test Project", description: str = "This is a test project") -> Dict[str, Any]:
        project_create = ProjectCreate(project_title=title, project_description=description)
        response = client.post("/projects/", json=project_create.dict())
        assert response.status_code == 200
        return response.json()
    return _create_project

@pytest.mark.parametrize("title,description", [
    ("Test Project", "This is a test project"),
    ("Another Project", "This is another test project"),
])
def test_create_project(client: TestClient, title: str, description: str) -> None:
    project_create = ProjectCreate(project_title=title, project_description=description)
    response = client.post("/projects/", json=project_create.dict())
    assert response.status_code == 200
    data = ProjectResponse(**response.json())
    assert data.project_title == title
    assert data.project_description == description
    assert data.project_id is not None

def test_read_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = ProjectResponse(**response.json())
    assert data.project_title == project["project_title"]
    assert data.project_description == project["project_description"]
    assert data.project_id == project_id

def test_update_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    updated_title = "Updated Project"
    updated_description = "This project has been updated"
    project_update = ProjectUpdate(project_title=updated_title, project_description=updated_description)
    response = client.put(f"/projects/{project_id}", json=project_update.dict())
    assert response.status_code == 200
    data = ProjectResponse(**response.json())
    assert data.project_title == updated_title
    assert data.project_description == updated_description
    assert data.project_id == project_id

# ... (rest of the test functions remain similar, just update the model usage)

def test_error_handling(client: TestClient) -> None:
    # Test non-existent project
    response = client.get("/projects/9999")
    assert response.status_code == 404
    assert "detail" in response.json()

    # Test invalid input
    invalid_project = ProjectCreate(project_title="", project_description="Invalid data")
    response = client.post("/projects/", json=invalid_project.dict())
    assert response.status_code == 422
    assert "detail" in response.json()

    # Test deleting non-existent project
    response = client.delete("/projects/9999")
    assert response.status_code == 404
    assert "detail" in response.json()
