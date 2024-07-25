import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..db.crud import DatabaseManager
from ..main import app, get_db
from ..db.schema import Base

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_database():
    # Drop and recreate tables before each test
    db_manager = DatabaseManager(engine)
    db_manager.drop_database(engine)
    db_manager.create_database(engine)
    yield
    # Drop tables after each test
    db_manager.drop_database(engine)

    # Clear all data from tables
    session = TestingSessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()

# Clear the database before running tests
DatabaseManager(engine).drop_database(engine)
DatabaseManager(engine)

def test_create_project():
    response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == "Test Project"
    assert data["project_description"] == "Test Description"
    assert "project_id" in data

def test_read_projects():
    # Create a project first
    client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    
    response = client.get("/projects/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

def test_read_project():
    # Create a project
    create_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 2", "project_description": "Test Description 2"}
    )
    project_id = create_response.json()["project_id"]

    # Read the project
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == "Test Project 2"
    assert data["project_description"] == "Test Description 2"

def test_update_project():
    # Create a project
    create_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 3", "project_description": "Test Description 3"}
    )
    project_id = create_response.json()["project_id"]

    # Update the project
    update_response = client.put(
        f"/projects/{project_id}",
        json={"project_title": "Updated Project", "project_description": "Updated Description"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["project_title"] == "Updated Project"
    assert data["project_description"] == "Updated Description"

def test_delete_project():
    # Create a project
    create_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 4", "project_description": "Test Description 4"}
    )
    project_id = create_response.json()["project_id"]

    # Delete the project
    delete_response = client.delete(f"/projects/{project_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Project deleted successfully"

    # Verify that the project is deleted
    get_response = client.get(f"/projects/{project_id}")
    assert get_response.status_code == 404

def test_create_code_type():
    # Create a project
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
    data = response.json()
    assert data["type_name"] == "Test CodeType"
    assert "type_id" in data

    # Try to create the same code type again in the same project
    response = client.post(
        "/code_types/",
        json={"type_name": "Test CodeType", "project_id": project_id}
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already exists" in data["detail"]

def test_read_code_types():
    # Create a project and a code type
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_id = project_response.json()["project_id"]
    client.post(
        "/code_types/",
        json={"type_name": "Test CodeType", "project_id": project_id}
    )

    response = client.get("/code_types/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

def test_search_elements():
    # Create necessary data (project, series, segment, element)
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

    import uuid
    unique_segment_title = f"Test Segment {uuid.uuid4()}"
    segment_response = client.post(
        "/segments/",
        json={"segment_title": unique_segment_title, "series_id": series_id, "project_id": project_id}
    )
    assert segment_response.status_code == 200, f"Failed to create segment: {segment_response.json()}"
    segment_id = segment_response.json().get("segment_id")
    assert segment_id is not None, f"segment_id is missing from response: {segment_response.json()}"

    element_response = client.post(
        "/elements/",
        json={"element_text": "Test Element", "segment_id": segment_id, "project_id": project_id}
    )
    assert element_response.status_code == 200, f"Failed to create element: {element_response.json()}"

    # Search for elements
    search_response = client.get("/search_elements/?search_term=Test")
    assert search_response.status_code == 200
    data = search_response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["element_text"] == "Test Element"

    # Check pagination headers
    assert "X-Total-Count" in search_response.headers
    assert "X-Limit" in search_response.headers
    assert "X-Skip" in search_response.headers

# Add more tests for other endpoints (Code, Series, Segment, Element, Annotation) following the same pattern
