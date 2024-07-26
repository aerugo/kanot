import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from kanot.db.schema import Base
from kanot.main import create_app

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app = create_app(SQLALCHEMY_DATABASE_URL)

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

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

def test_read_code_types():
    response = client.get("/code_types/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_codes():
    response = client.get("/codes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_series():
    # First, create a project
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 7", "project_description": "Project for series test"}
    )
    project_data = project_response.json()
    project_id = project_data["project_id"]

    # Then, create a series
    response = client.post(
        "/series/",
        json={"series_title": "Test Series", "project_id": project_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["series_title"] == "Test Series"
    assert data["project_id"] == project_id
    assert "series_id" in data

def test_create_segment():
    print("!!!!!!!!!Creating segment")
    # First, create a project
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 8", "project_description": "Project for segment test"}
    )
    project_data = project_response.json()
    project_id = project_data["project_id"]

    print(f"Project ID: {project_id}")

    # Then, create a series
    series_response = client.post(
        "/series/",
        json={"series_title": "Test Series 2", "project_id": project_id}
    )
    series_data = series_response.json()
    series_id = series_data["series_id"]

    # Finally, create a segment
    response = client.post(
        "/segments/",
        json={"segment_title": "Test Segment", "series_id": series_id, "project_id": project_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["segment_title"] == "Test Segment"
    assert data["series_id"] == series_id
    assert data["project_id"] == project_id
    assert "segment_id" in data

def test_create_element():
    # First, create a project
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 9", "project_description": "Project for element test"}
    )
    project_data = project_response.json()
    project_id = project_data["project_id"]

    # Then, create a series
    series_response = client.post(
        "/series/",
        json={"series_title": "Test Series 3", "project_id": project_id}
    )
    series_data = series_response.json()
    series_id = series_data["series_id"]

    # Create a segment
    segment_response = client.post(
        "/segments/",
        json={"segment_title": "Test Segment 2", "series_id": series_id, "project_id": project_id}
    )
    segment_data = segment_response.json()
    segment_id = segment_data["segment_id"]

    # Finally, create an element
    response = client.post(
        "/elements/",
        json={"element_text": "Test Element", "segment_id": segment_id, "project_id": project_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["element_text"] == "Test Element"
    assert data["segment_id"] == segment_id
    assert data["project_id"] == project_id
    assert "element_id" in data

def test_create_annotation():
    # First, create a project
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 10", "project_description": "Project for annotation test"}
    )
    project_data = project_response.json()
    project_id = project_data["project_id"]

    # Create a code type
    code_type_response = client.post(
        "/code_types/",
        json={"type_name": "Test Code Type 3", "project_id": project_id}
    )
    code_type_data = code_type_response.json()
    type_id = code_type_data["type_id"]

    # Create a code
    code_response = client.post(
        "/codes/",
        json={
            "term": "Test Code 2",
            "description": "This is another test code",
            "type_id": type_id,
            "reference": "Test reference 2",
            "coordinates": "Test coordinates 2",
            "project_id": project_id
        }
    )
    code_data = code_response.json()
    code_id = code_data["code_id"]

    # Create an element
    element_response = client.post(
        "/elements/",
        json={"element_text": "Test Element 2", "segment_id": 1, "project_id": project_id}
    )
    element_data = element_response.json()
    element_id = element_data["element_id"]

    # Finally, create an annotation
    response = client.post(
        "/annotations/",
        json={"element_id": element_id, "code_id": code_id, "project_id": project_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["element_id"] == element_id
    assert data["code_id"] == code_id
    assert "annotation_id" in data

def test_search_elements():
    response = client.get("/search_elements/?search_term=Test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "element_id" in data[0]
    assert "element_text" in data[0]

def test_merge_codes():
    # First, create two codes
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 11", "project_description": "Project for merge codes test"}
    )
    project_data = project_response.json()
    project_id = project_data["project_id"]

    code_type_response = client.post(
        "/code_types/",
        json={"type_name": "Test Code Type 4", "project_id": project_id}
    )
    code_type_data = code_type_response.json()
    type_id = code_type_data["type_id"]

    code1_response = client.post(
        "/codes/",
        json={
            "term": "Test Code 3",
            "description": "This is a test code for merging",
            "type_id": type_id,
            "reference": "Test reference 3",
            "coordinates": "Test coordinates 3",
            "project_id": project_id
        }
    )
    code1_data = code1_response.json()
    code1_id = code1_data["code_id"]

    code2_response = client.post(
        "/codes/",
        json={
            "term": "Test Code 4",
            "description": "This is another test code for merging",
            "type_id": type_id,
            "reference": "Test reference 4",
            "coordinates": "Test coordinates 4",
            "project_id": project_id
        }
    )
    code2_data = code2_response.json()
    code2_id = code2_data["code_id"]

    # Then, merge the codes
    response = client.post(f"/merge_codes/?code_a_id={code1_id}&code_b_id={code2_id}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Successfully merged Code {code1_id} into Code {code2_id}" in data["message"]

    # Verify that code1 no longer exists
    code1_get_response = client.get(f"/codes/{code1_id}")
    assert code1_get_response.status_code == 404

    # Verify that code2 still exists
    code2_get_response = client.get(f"/codes/{code2_id}")
    assert code2_get_response.status_code == 200
