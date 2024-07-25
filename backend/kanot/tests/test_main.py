import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..db.crud import DatabaseManager
from ..main import app, get_db

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
DatabaseManager(engine).drop_database(engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    # Create tables
    DatabaseManager(engine)
    yield
    # Drop tables after tests
    DatabaseManager(engine).drop_database(engine)

# Test Project endpoints
def test_create_project(test_db):
    response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == "Test Project"
    assert data["project_description"] == "Test Description"
    assert "project_id" in data

def test_read_projects(test_db):
    response = client.get("/projects/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_read_project(test_db):
    # First, create a project
    create_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 2", "project_description": "Test Description 2"}
    )
    project_id = create_response.json()["project_id"]

    # Then, read the project
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == "Test Project 2"
    assert data["project_description"] == "Test Description 2"

def test_update_project(test_db):
    # First, create a project
    create_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 3", "project_description": "Test Description 3"}
    )
    project_id = create_response.json()["project_id"]

    # Then, update the project
    update_response = client.put(
        f"/projects/{project_id}",
        json={"project_title": "Updated Project", "project_description": "Updated Description"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["project_title"] == "Updated Project"
    assert data["project_description"] == "Updated Description"

def test_delete_project(test_db):
    # First, create a project
    create_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 4", "project_description": "Test Description 4"}
    )
    project_id = create_response.json()["project_id"]

    # Then, delete the project
    delete_response = client.delete(f"/projects/{project_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Project deleted successfully"

    # Verify that the project is deleted
    get_response = client.get(f"/projects/{project_id}")
    assert get_response.status_code == 404

# Test CodeType endpoints
def test_create_code_type(test_db):
    # First, create a project
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_id = project_response.json()["project_id"]

    # Create a code type
    response = client.post(
        "/code_types/",
        json={"type_name": "Test CodeType", "project_id": project_id}
    )
    assert response.status_code == 200

    # Try to create the same code type again
    response = client.post(
        "/code_types/",
        json={"type_name": "Test CodeType", "project_id": project_id}
    )
    assert response.status_code == 200  # It should still return 200 as we're returning the existing code type
    data = response.json()
    assert data["type_name"] == "Test CodeType"
    assert "type_id" in data

def test_read_code_types(test_db):
    response = client.get("/code_types/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

# Add more tests for other endpoints (Code, Series, Segment, Element, Annotation) following the same pattern

# Test search_elements endpoint
def test_search_elements(test_db):
    # First, create necessary data (project, series, segment, element)
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_id = project_response.json()["project_id"]

    series_response = client.post(
        "/series/",
        json={"series_title": "Test Series", "project_id": project_id}
    )
    series_id = series_response.json()["series_id"]

    segment_response = client.post(
        "/segments/",
        json={"segment_title": "Test Segment", "series_id": series_id, "project_id": project_id}
    )
    segment_id = segment_response.json()["segment_id"]

    element_response = client.post(
        "/elements/",
        json={"element_text": "Test Element", "segment_id": segment_id, "project_id": project_id}
    )

    # Then, search for elements
    search_response = client.get("/search_elements/?search_term=Test")
    assert search_response.status_code == 200
    data = search_response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["element_text"] == "Test Element"

    # Check pagination headers
    assert "X-Total-Count" in search_response.headers
    assert "X-Limit" in search_response.headers
    assert "X-Skip" in search_response.headers

# Add more complex test scenarios as needed
