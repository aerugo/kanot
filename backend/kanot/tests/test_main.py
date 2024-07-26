import pytest
from fastapi.testclient import TestClient

from kanot.db.crud import DatabaseManager
from kanot.main import app, get_db


def test_create_project(client: TestClient, test_db: DatabaseManager):
    response = client.post("/projects/", json={"project_title": "Test Project", "project_description": "Test Description"})
    assert response.status_code == 200
    assert response.json()["project_title"] == "Test Project"
    assert response.json()["project_description"] == "Test Description"

def test_read_projects(client: TestClient, test_db: DatabaseManager):
    with test_db.get_session() as session:
        test_db.create_project(session, "Test Project 1", "Test Description 1")
        test_db.create_project(session, "Test Project 2", "Test Description 2")
    
    response = client.get("/projects/")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) == 2
    assert projects[0]["project_title"] == "Test Project 1"
    assert projects[1]["project_title"] == "Test Project 2"

def test_read_project(client: TestClient, test_db: DatabaseManager):
    with test_db.get_session() as session:
        project = test_db.create_project(session, "Test Project", "Test Description")
        project_id = project.project_id

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["project_title"] == "Test Project"
    assert response.json()["project_description"] == "Test Description"

def test_update_project(client: TestClient, test_db: DatabaseManager):
    with test_db.get_session() as session:
        project = test_db.create_project(session, "Old Title", "Old Description")
        project_id = project.project_id

    response = client.put(f"/projects/{project_id}", json={"project_title": "New Title", "project_description": "New Description"})
    assert response.status_code == 200
    assert response.json()["project_title"] == "New Title"
    assert response.json()["project_description"] == "New Description"

def test_delete_project(client: TestClient, test_db: DatabaseManager):
    with test_db.get_session() as session:
        project = test_db.create_project(session, "Test Project", "Test Description")
        project_id = project.project_id

    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Project deleted successfully"

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 404

def test_create_code_type(client: TestClient, test_db: DatabaseManager):
    with test_db.get_session() as session:
        project = test_db.create_project(session, "Test Project", "Test Description")
        project_id = project.project_id

    response = client.post("/code_types/", json={"type_name": "Test CodeType", "project_id": project_id})
    assert response.status_code == 200
    assert response.json()["type_name"] == "Test CodeType"
    assert response.json()["project_id"] == project_id

def test_read_code_types(client: TestClient, test_db: DatabaseManager):
    with test_db.get_session() as session:
        project = test_db.create_project(session, "Test Project", "Test Description")
        project_id = project.project_id
        test_db.create_code_type(session, "Test CodeType 1", project_id)
        test_db.create_code_type(session, "Test CodeType 2", project_id)

    response = client.get("/code_types/")
    assert response.status_code == 200
    code_types = response.json()
    assert len(code_types) == 2
    assert code_types[0]["type_name"] == "Test CodeType 1"
    assert code_types[1]["type_name"] == "Test CodeType 2"

def test_read_code_type(client: TestClient, test_db: DatabaseManager):
    with test_db.get_session() as session:
        project = test_db.create_project(session, "Test Project", "Test Description")
        project_id = project.project_id
        code_type = test_db.create_code_type(session, "Test CodeType", project_id)
        type_id = code_type.type_id

    response = client.get(f"/code_types/{type_id}")
    assert response.status_code == 200
    assert response.json()["type_name"] == "Test CodeType"
    assert response.json()["project_id"] == project_id

def test_update_code_type(client: TestClient, test_db: DatabaseManager):
    with test_db.get_session() as session:
        project = test_db.create_project(session, "Test Project", "Test Description")
        project_id = project.project_id
        code_type = test_db.create_code_type(session, "Old CodeType", project_id)
        type_id = code_type.type_id

    response = client.put(f"/code_types/{type_id}", json={"type_name": "New CodeType", "project_id": project_id})
    assert response.status_code == 200
    assert response.json()["type_name"] == "New CodeType"

def test_delete_code_type(client: TestClient, test_db: DatabaseManager):
    with test_db.get_session() as session:
        project = test_db.create_project(session, "Test Project", "Test Description")
        project_id = project.project_id
        code_type = test_db.create_code_type(session, "Test CodeType", project_id)
        type_id = code_type.type_id

    response = client.delete(f"/code_types/{type_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Code type deleted successfully"

    response = client.get(f"/code_types/{type_id}")
    assert response.status_code == 404
