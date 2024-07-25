import uuid
from typing import Any, Dict, List, Optional

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..db.crud import DatabaseManager
from ..db.schema import Base
from ..main import app, get_db


# Pydantic models for response validation
class ProjectResponse(BaseModel):
    project_id: int
    project_title: str
    project_description: Optional[str]

class CodeTypeResponse(BaseModel):
    type_id: int
    type_name: str
    project_id: int

class CodeResponse(BaseModel):
    code_id: int
    term: str
    description: Optional[str]
    type_id: int
    reference: Optional[str]
    coordinates: Optional[str]
    project_id: int

class SeriesResponse(BaseModel):
    series_id: int
    series_title: str
    project_id: int

class SegmentResponse(BaseModel):
    segment_id: int
    segment_title: str
    series_id: int
    project_id: int

class ElementResponse(BaseModel):
    element_id: int
    element_text: str
    segment_id: int
    project_id: int

# Setup test database
TEST_DB_URL: str = "sqlite:///./test.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
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
def reset_database() -> None:
    # Drop and recreate tables before each test
    db_manager = DatabaseManager(engine)
    db_manager.drop_database(engine)
    db_manager.create_database(engine)
    
    # Clear all data from tables
    session = TestingSessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()
    
    yield
    
    # Drop tables after each test
    db_manager.drop_database(engine)

# Clear the database before running tests
DatabaseManager(engine).drop_database(engine)
DatabaseManager(engine)

def test_create_project() -> None:
    response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    assert response.status_code == 200
    data = ProjectResponse.model_validate(response.json())
    assert data.project_title == "Test Project"
    assert data.project_description == "Test Description"
    assert data.project_id is not None

def test_read_projects() -> None:
    # Create a project first
    initial_response = client.get("/projects/")
    initial_count = len(initial_response.json())

    client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    
    response = client.get("/projects/")
    assert response.status_code == 200
    data = [ProjectResponse.model_validate(item) for item in response.json()]
    assert isinstance(data, list)
    assert len(data) == initial_count + 1

def test_read_project() -> None:
    # Create a project
    create_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 2", "project_description": "Test Description 2"}
    )
    project_data = ProjectResponse.model_validate(create_response.json())

    # Read the project
    response = client.get(f"/projects/{project_data.project_id}")
    assert response.status_code == 200
    data = ProjectResponse.model_validate(response.json())
    assert data.project_title == "Test Project 2"
    assert data.project_description == "Test Description 2"

def test_update_project() -> None:
    # Create a project
    create_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 3", "project_description": "Test Description 3"}
    )
    project_data = ProjectResponse.model_validate(create_response.json())

    # Update the project
    update_response = client.put(
        f"/projects/{project_data.project_id}",
        json={"project_title": "Updated Project", "project_description": "Updated Description"}
    )
    assert update_response.status_code == 200
    data = ProjectResponse.model_validate(update_response.json())
    assert data.project_title == "Updated Project"
    assert data.project_description == "Updated Description"

def test_delete_project() -> None:
    # Create a project
    create_response = client.post(
        "/projects/",
        json={"project_title": "Test Project 4", "project_description": "Test Description 4"}
    )
    project_data = ProjectResponse.model_validate(create_response.json())

    # Delete the project
    delete_response = client.delete(f"/projects/{project_data.project_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Project deleted successfully"

    # Verify that the project is deleted
    get_response = client.get(f"/projects/{project_data.project_id}")
    assert get_response.status_code == 404

def test_create_code_type() -> None:
    # Create a project
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_data = ProjectResponse.model_validate(project_response.json())

    # Create a code type
    response = client.post(
        "/code_types/",
        json={"type_name": "Test CodeType", "project_id": project_data.project_id}
    )
    assert response.status_code == 200
    data = CodeTypeResponse.model_validate(response.json())
    assert data.type_name == "Test CodeType"
    assert data.type_id is not None

    # Try to create the same code type again in the same project
    response = client.post(
        "/code_types/",
        json={"type_name": "Test CodeType", "project_id": project_data.project_id}
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in str(data)
    assert "already exists" in response.json()["detail"]

def test_read_code_types() -> None:
    # Get initial count of code types
    initial_response = client.get("/code_types/")
    initial_count = len(initial_response.json())

    # Create a project and a code type
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_data = ProjectResponse.model_validate(project_response.json())
    client.post(
        "/code_types/",
        json={"type_name": "Test CodeType", "project_id": project_data.project_id}
    )

    response = client.get("/code_types/")
    assert response.status_code == 200
    data = [CodeTypeResponse.model_validate(item) for item in response.json()]
    assert isinstance(data, list)
    assert len(data) == initial_count + 1

def test_create_code() -> None:
    # Create a project and code type first
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_data = ProjectResponse.model_validate(project_response.json())
    
    code_type_response = client.post(
        "/code_types/",
        json={"type_name": "Test CodeType", "project_id": project_data.project_id}
    )
    code_type_data = CodeTypeResponse.model_validate(code_type_response.json())

    # Create a code
    response = client.post(
        "/codes/",
        json={
            "term": "Test Code",
            "description": "Test Description",
            "type_id": code_type_data.type_id,
            "reference": "Test Reference",
            "coordinates": "Test Coordinates",
            "project_id": project_data.project_id
        }
    )
    assert response.status_code == 200
    data = CodeResponse.model_validate(response.json())
    assert data.term == "Test Code"
    assert data.code_id is not None

def test_read_codes() -> None:
    # Create a project, code type, and code first
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_data = ProjectResponse.model_validate(project_response.json())
    
    code_type_response = client.post(
        "/code_types/",
        json={"type_name": "Test CodeType", "project_id": project_data.project_id}
    )
    code_type_data = CodeTypeResponse.model_validate(code_type_response.json())

    client.post(
        "/codes/",
        json={
            "term": "Test Code",
            "description": "Test Description",
            "type_id": code_type_data.type_id,
            "reference": "Test Reference",
            "coordinates": "Test Coordinates",
            "project_id": project_data.project_id
        }
    )

    response = client.get("/codes/")
    assert response.status_code == 200
    data = [CodeResponse.model_validate(item) for item in response.json()]
    assert isinstance(data, list)
    assert len(data) >= 1

def test_create_series() -> None:
    # Create a project first
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_data = ProjectResponse.model_validate(project_response.json())

    # Create a series
    response = client.post(
        "/series/",
        json={"series_title": "Test Series", "project_id": project_data.project_id}
    )
    assert response.status_code == 200
    data = SeriesResponse.model_validate(response.json())
    assert data.series_title == "Test Series"
    assert data.series_id is not None

def test_read_series() -> None:
    # Create a project and series first
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_data = ProjectResponse.model_validate(project_response.json())

    client.post(
        "/series/",
        json={"series_title": "Test Series", "project_id": project_data.project_id}
    )

    response = client.get("/series/")
    assert response.status_code == 200
    data = [SeriesResponse.model_validate(item) for item in response.json()]
    assert isinstance(data, list)
    assert len(data) >= 1

def test_create_segment() -> None:
    # Create a project and series first
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_data = ProjectResponse.model_validate(project_response.json())

    series_response = client.post(
        "/series/",
        json={"series_title": "Test Series", "project_id": project_data.project_id}
    )
    series_data = SeriesResponse.model_validate(series_response.json())

    # Create a segment
    unique_segment_title = f"Test Segment {uuid.uuid4()}"
    response = client.post(
        "/segments/",
        json={"segment_title": unique_segment_title, "series_id": series_data.series_id, "project_id": project_data.project_id}
    )
    assert response.status_code == 200
    data = SegmentResponse.model_validate(response.json())
    assert data.segment_title == unique_segment_title
    assert data.segment_id is not None

def test_read_segments() -> None:
    # Create a project, series, and segment first
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_data = ProjectResponse.model_validate(project_response.json())

    series_response = client.post(
        "/series/",
        json={"series_title": "Test Series", "project_id": project_data.project_id}
    )
    series_data = SeriesResponse.model_validate(series_response.json())

    unique_segment_title = f"Test Segment {uuid.uuid4()}"
    client.post(
        "/segments/",
        json={"segment_title": unique_segment_title, "series_id": series_data.series_id, "project_id": project_data.project_id}
    )

    response = client.get("/segments/")
    assert response.status_code == 200
    data = [SegmentResponse.model_validate(item) for item in response.json()]
    assert isinstance(data, list)
    assert len(data) >= 1

def test_create_element() -> None:
    # Create a project, series, and segment first
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_data = ProjectResponse.model_validate(project_response.json())

    series_response = client.post(
        "/series/",
        json={"series_title": "Test Series", "project_id": project_data.project_id}
    )
    series_data = SeriesResponse.model_validate(series_response.json())

    unique_segment_title = f"Test Segment {uuid.uuid4()}"
    segment_response = client.post(
        "/segments/",
        json={"segment_title": unique_segment_title, "series_id": series_data.series_id, "project_id": project_data.project_id}
    )
    segment_data = SegmentResponse.model_validate(segment_response.json())

    # Create an element
    response = client.post(
        "/elements/",
        json={"element_text": "Test Element", "segment_id": segment_data.segment_id, "project_id": project_data.project_id}
    )
    assert response.status_code == 200
    data = ElementResponse.model_validate(response.json())
    assert data.element_text == "Test Element"
    assert data.element_id is not None

def test_read_elements() -> None:
    # Create a project, series, segment, and element first
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_data = ProjectResponse.model_validate(project_response.json())

    series_response = client.post(
        "/series/",
        json={"series_title": "Test Series", "project_id": project_data.project_id}
    )
    series_data = SeriesResponse.model_validate(series_response.json())

    unique_segment_title = f"Test Segment {uuid.uuid4()}"
    segment_response = client.post(
        "/segments/",
        json={"segment_title": unique_segment_title, "series_id": series_data.series_id, "project_id": project_data.project_id}
    )
    segment_data = SegmentResponse.model_validate(segment_response.json())

    client.post(
        "/elements/",
        json={"element_text": "Test Element", "segment_id": segment_data.segment_id, "project_id": project_data.project_id}
    )

    response = client.get("/elements/")
    assert response.status_code == 200
    data = [ElementResponse.model_validate(item) for item in response.json()]
    assert isinstance(data, list)
    assert len(data) >= 1

def test_search_elements() -> None:
    # Create necessary data (project, series, segment, element)
    project_response = client.post(
        "/projects/",
        json={"project_title": "Test Project", "project_description": "Test Description"}
    )
    project_data = ProjectResponse.model_validate(project_response.json())

    series_response = client.post(
        "/series/",
        json={"series_title": "Test Series", "project_id": project_data.project_id}
    )
    series_data = SeriesResponse.model_validate(series_response.json())

    unique_segment_title = f"Test Segment {uuid.uuid4()}"
    segment_response = client.post(
        "/segments/",
        json={"segment_title": unique_segment_title, "series_id": series_data.series_id, "project_id": project_data.project_id}
    )
    assert segment_response.status_code == 200, f"Failed to create segment: {segment_response.json()}"
    segment_data = SegmentResponse.model_validate(segment_response.json())
    assert segment_data.segment_id is not None, f"segment_id is missing from response: {segment_response.json()}"

    element_response = client.post(
        "/elements/",
        json={"element_text": "Test Element", "segment_id": segment_data.segment_id, "project_id": project_data.project_id}
    )
    assert element_response.status_code == 200, f"Failed to create element: {element_response.json()}"
    element_data = ElementResponse.model_validate(element_response.json())

    print(f"Created element: {element_data}")

    # Add a small delay to ensure the element is indexed
    import time
    time.sleep(0.5)

    # Search for elements
    search_response = client.get(f"/search_elements/?search_term={element_data.element_text}&limit=1000")
    assert search_response.status_code == 200
    search_data: List[Dict[str, Any]] = search_response.json()
    assert isinstance(search_data, list)
    
    print(f"Search results: {search_data}")

    assert len(search_data) >= 1, f"No search results found for term: {element_data.element_text}"

    # Inspect the structure of the first element
    if search_data:
        first_element: Dict[str, Any] = search_data[0]
        print(f"Structure of first element: {first_element}")

        # Check if 'element_text' is directly in the element or nested
        if "element_text" in first_element:
            assert any(element["element_text"] == element_data.element_text for element in search_data), f"Expected element '{element_data.element_text}' not found in search results: {search_data}"
        elif "element" in first_element and "element_text" in first_element["element"]:
            assert any(element["element"]["element_text"] == element_data.element_text for element in search_data), f"Expected element '{element_data.element_text}' not found in nested structure: {search_data}"
        else:
            pytest.fail(f"Unexpected element structure. 'element_text' not found. Element structure: {first_element}")

    # Check pagination headers
    headers: Dict[str, str] = dict(search_response.headers)
    print(f"Response headers: {headers}")
    assert "x-total-count" in headers  # Change this line to lowercase
    assert "x-limit" in headers
    assert "x-skip" in headers
    assert int(headers["x-total-count"]) >= 1
    assert int(headers["x-limit"]) == 1000
    assert int(headers["x-skip"]) == 0

    # Additional check to ensure the created element is in the search results
    found_element = next((element for element in search_data if element.get("element_id") == element_data.element_id), None)
    assert found_element is not None, f"Created element with id {element_data.element_id} not found in search results"
    print(f"Found element in search results: {found_element}")

# You can add more test functions here as needed