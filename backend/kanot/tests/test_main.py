import pytest
from fastapi.testclient import TestClient

from kanot.main import create_app

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

app = create_app(SQLALCHEMY_DATABASE_URL)
client = TestClient(app)

def create_project(client, title="Test Project", description="This is a test project"):
    response = client.post(
        "/projects/",
        json={"project_title": title, "project_description": description}
    )
    return response.json()

def create_code_type(client, type_name, project_id):
    response = client.post(
        "/code_types/",
        json={"type_name": type_name, "project_id": project_id}
    )
    return response.json()

def create_code(client, term, description, type_id, reference, coordinates, project_id):
    response = client.post(
        "/codes/",
        json={
            "term": term,
            "description": description,
            "type_id": type_id,
            "reference": reference,
            "coordinates": coordinates,
            "project_id": project_id
        }
    )
    return response.json()

def create_series(client, title, project_id):
    response = client.post(
        "/series/",
        json={"series_title": title, "project_id": project_id}
    )
    return response.json()

def create_segment(client, title, series_id, project_id):
    response = client.post(
        "/segments/",
        json={"segment_title": title, "series_id": series_id, "project_id": project_id}
    )
    return response.json()

def create_element(client, text, segment_id, project_id):
    response = client.post(
        "/elements/",
        json={"element_text": text,  "segment_id": segment_id, "project_id": project_id}
    )
    return response.json()

def create_annotation(client, element_id, code_id, project_id):
    response = client.post(
        "/annotations/",
        json={"element_id": element_id, "code_id": code_id, "project_id": project_id}
    )
    return response.json()

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
    project = create_project(client, "Test Project 2", "This is another test project")
    project_id = project["project_id"]

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == "Test Project 2"
    assert data["project_description"] == "This is another test project"
    assert data["project_id"] == project_id

def test_update_project():
    project = create_project(client, "Test Project 3", "This is yet another test project")
    project_id = project["project_id"]

    response = client.put(
        f"/projects/{project_id}",
        json={"project_title": "Updated Test Project 3", "project_description": "This project has been updated"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == "Updated Test Project 3"
    assert data["project_description"] == "This project has been updated"
    assert data["project_id"] == project_id

def test_delete_project():
    project = create_project(client, "Test Project 4", "This project will be deleted")
    project_id = project["project_id"]

    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Project deleted successfully"}

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 404

def test_create_code_type():
    project = create_project(client, "Test Project 5", "Project for code type test")
    project_id = project["project_id"]

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
    project = create_project(client, "Test Project 6", "Project for code test")
    project_id = project["project_id"]

    code_type = create_code_type(client, "Test Code Type 2", project_id)
    type_id = code_type["type_id"]

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

def test_read_code_types():
    response = client.get("/code_types/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_codes():
    response = client.get("/codes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_series():
    project = create_project(client, "Test Project 7", "Project for series test")
    project_id = project["project_id"]

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
    project = create_project(client, "Test Project 8", "Project for segment test")
    project_id = project["project_id"]

    series = create_series(client, "Test Series 2", project_id)
    series_id = series["series_id"]

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
    project = create_project(client, "Test Project 9", "Project for element test")
    project_id = project["project_id"]

    series = create_series(client, "Test Series 3", project_id)
    series_id = series["series_id"]

    segment = create_segment(client, "Test Segment 2", series_id, project_id)
    segment_id = segment["segment_id"]

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
    project = create_project(client, "Test Project 10", "Project for annotation test")
    project_id = project["project_id"]

    code_type = create_code_type(client, "Test Code Type 3", project_id)
    type_id = code_type["type_id"]

    code = create_code(client, "Test Code 2", "This is another test code", type_id, "Test reference 2", "Test coordinates 2", project_id)
    code_id = code["code_id"]

    series = create_series(client, "Test Series 4", project_id)
    series_id = series["series_id"]

    segment = create_segment(client, "Test Segment 3", series_id, project_id)
    segment_id = segment["segment_id"]

    element = create_element(client, "Test Element 2", segment_id, project_id)
    element_id = element["element_id"]

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
    project = create_project(client, "Test Project 11", "Project for search test")
    project_id = project["project_id"]

    series = create_series(client, "Test Series 5", project_id)
    series_id = series["series_id"]

    segment = create_segment(client, "Test Segment 4", series_id, project_id)
    segment_id = segment["segment_id"]

    create_element(client, "Test Element for Search", segment_id, project_id)

    response = client.get("/search_elements/?search_term=Test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "element_id" in data[0]
    assert "element_text" in data[0]

def test_merge_codes():
    project = create_project(client, "Test Project 12", "Project for merge codes test")
    project_id = project["project_id"]

    code_type = create_code_type(client, "Test Code Type 4", project_id)
    type_id = code_type["type_id"]

    code1 = create_code(client, "Test Code 3", "This is a test code for merging", type_id, "Test reference 3", "Test coordinates 3", project_id)
    code1_id = code1["code_id"]

    code2 = create_code(client, "Test Code 4", "This is another test code for merging", type_id, "Test reference 4", "Test coordinates 4", project_id)
    code2_id = code2["code_id"]

    response = client.post(f"/merge_codes/?code_a_id={code1_id}&code_b_id={code2_id}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Successfully merged Code {code1_id} into Code {code2_id}" in data["message"]

    response = client.get(f"/codes/{code1_id}")
    assert response.status_code == 404

    response = client.get(f"/codes/{code2_id}")
    assert response.status_code == 200
