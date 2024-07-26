import pytest
from fastapi.testclient import TestClient

from kanot.main import create_app

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

app = create_app(SQLALCHEMY_DATABASE_URL)
client = TestClient(app)

def test_create_project():
    response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "This is a test project"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == "Test Project"
    assert data["project_description"] == "This is a test project"
    assert "project_id" in data

def test_read_project():
    # First, create a project
    create_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 2", "project_description": "This is another test project"}
    )
    create_data = create_response.json()
    project_id = create_data["project_id"]

    # Then, read the project
    read_response = client.get(f"/projects/{project_id}")
    assert read_response.status_code == 200
    read_data = read_response.json()
    assert read_data["project_title"] == "Test Project 2"
    assert read_data["project_description"] == "This is another test project"
    assert read_data["project_id"] == project_id

def test_update_project():
    # First, create a project
    create_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 3", "project_description": "This is yet another test project"}
    )
    create_data = create_response.json()
    project_id = create_data["project_id"]

    # Then, update the project
    update_response = client.put(
        f"/projects/{project_id}",
        json={"project_title": "Updated Test Project 3", "project_description": "This project has been updated"}
    )
    assert update_response.status_code == 200
    update_data = update_response.json()
    assert update_data["project_title"] == "Updated Test Project 3"
    assert update_data["project_description"] == "This project has been updated"
    assert update_data["project_id"] == project_id

def test_delete_project():
    # First, create a project
    create_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 4", "project_description": "This project will be deleted"}
    )
    create_data = create_response.json()
    project_id = create_data["project_id"]

    # Then, delete the project
    delete_response = client.delete(f"/projects/{project_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Project deleted successfully"}

    # Verify that the project no longer exists
    read_response = client.get(f"/projects/{project_id}")
    assert read_response.status_code == 404

def test_create_code_type():
    # First, create a project
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 5", "project_description": "Project for code type test"}
    )
    project_data = project_response.json()
    project_id = project_data["project_id"]

    # Then, create a code type
    response = client.post(
        "/code_types/",
        json={"type_name": "Test Code Type", "project_id": project_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type_name"] == "Test Code Type"
    assert data["project_id"] == project_id
    assert "type_id" in data

def test_create_code():
    # First, create a project
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 6", "project_description": "Project for code test"}
    )
    project_data = project_response.json()
    project_id = project_data["project_id"]

    # Then, create a code type
    code_type_response = client.post(
        "/code_types/",
        json={"type_name": "Test Code Type 2", "project_id": project_id}
    )
    code_type_data = code_type_response.json()
    type_id = code_type_data["type_id"]

    # Finally, create a code
    response = client.post(
        "/codes/",
        json={
            "term": "Test Code",
            "description": "This is a test code",
            "type_id": type_id,
            "reference": "Test reference",
            "coordinates": "Test coordinates",
            "project_id": project_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["term"] == "Test Code"
    assert data["description"] == "This is a test code"
    assert data["type_id"] == type_id
    assert data["reference"] == "Test reference"
    assert data["coordinates"] == "Test coordinates"
    assert data["project_id"] == project_id
    assert "code_id" in data

# Add more tests for other endpoints as needed
