import pytest
from typing import Callable, Dict, Any
from fastapi.testclient import TestClient


@pytest.fixture
def create_project(client: TestClient) -> Callable[[str, str], Dict[str, Any]]:
    def _create_project(title: str = "Test Project", description: str = "This is a test project") -> Dict[str, Any]:
        response = client.post(
            "/projects/",
            json={"project_title": title, "project_description": description}
        )
        assert response.status_code == 200
        return response.json()
    return _create_project

@pytest.mark.parametrize("title,description", [
    ("Test Project", "This is a test project"),
    ("Another Project", "This is another test project"),
])
def test_create_project(client: TestClient, title: str, description: str) -> None:
    response = client.post(
        "/projects/",
        json={"project_title": title, "project_description": description}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == title
    assert data["project_description"] == description
    assert "project_id" in data

def test_read_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == project["project_title"]
    assert data["project_description"] == project["project_description"]
    assert data["project_id"] == project_id

def test_update_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    updated_title = "Updated Project"
    updated_description = "This project has been updated"
    response = client.put(
        f"/projects/{project_id}",
        json={"project_title": updated_title, "project_description": updated_description}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == updated_title
    assert data["project_description"] == updated_description
    assert data["project_id"] == project_id

def test_update_code_type(client: TestClient, create_code_type: Callable[..., Dict[str, Any]]) -> None:
    code_type = create_code_type()
    type_id = code_type["type_id"]

    updated_name = "Updated Code Type"
    response = client.put(
        f"/code_types/{type_id}",
        json={"type_name": updated_name, "project_id": code_type["project_id"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type_name"] == updated_name
    assert data["type_id"] == type_id

def test_update_code(client: TestClient, create_code: Callable[..., Dict[str, Any]]) -> None:
    code = create_code()
    code_id = code["code_id"]

    updated_term = "Updated Code"
    updated_description = "This code has been updated"
    response = client.put(
        f"/codes/{code_id}",
        json={"term": updated_term, "description": updated_description}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["term"] == updated_term
    assert data["description"] == updated_description
    assert data["code_id"] == code_id

def test_update_series(client: TestClient, create_series: Callable[..., Dict[str, Any]]) -> None:
    series = create_series()
    series_id = series["series_id"]

    updated_title = "Updated Series"
    response = client.put(
        f"/series/{series_id}",
        json={"series_title": updated_title}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["series_title"] == updated_title
    assert data["series_id"] == series_id

def test_update_segment(client: TestClient, create_segment: Callable[..., Dict[str, Any]]) -> None:
    segment = create_segment()
    segment_id = segment["segment_id"]

    updated_title = "Updated Segment"
    response = client.put(
        f"/segments/{segment_id}",
        json={"segment_title": updated_title}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["segment_title"] == updated_title
    assert data["segment_id"] == segment_id
    assert "series_id" in data
    assert "project_id" in data

def test_update_element(client: TestClient, create_element: Callable[..., Dict[str, Any]]) -> None:
    element = create_element()
    element_id = element["element_id"]

    updated_text = "Updated Element Text"
    response = client.put(
        f"/elements/{element_id}",
        json={"element_text": updated_text}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["element_text"] == updated_text
    assert data["element_id"] == element_id
    assert "segment_id" in data
    assert "project_id" in data

def test_update_annotation(client: TestClient, create_annotation: Callable[..., Dict[str, Any]], create_code: Callable[..., Dict[str, Any]]) -> None:
    annotation = create_annotation()
    annotation_id = annotation["annotation_id"]

    # Create a new code to update the annotation with
    new_code = create_code()
    new_code_id = new_code["code_id"]

    response = client.put(
        f"/annotations/{annotation_id}",
        json={"code_id": new_code_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code_id"] == new_code_id
    assert data["annotation_id"] == annotation_id
    assert "element_id" in data

def test_delete_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Project deleted successfully"}

    # Verify that the project no longer exists
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 404

@pytest.fixture
def create_code_type(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> Callable[[str], Dict[str, Any]]:
    def _create_code_type(type_name: str = "Test Code Type") -> Dict[str, Any]:
        project = create_project()
        response = client.post(
            "/code_types/",
            json={"type_name": type_name, "project_id": project["project_id"]}
        )
        assert response.status_code == 200
        return response.json()
    return _create_code_type

def test_create_code_type(create_code_type: Callable[..., Dict[str, Any]]) -> None:
    code_type = create_code_type()
    assert code_type["type_name"] == "Test Code Type"
    assert "type_id" in code_type
    assert "project_id" in code_type

@pytest.fixture
def create_code(client: TestClient, create_project: Callable[..., Dict[str, Any]], create_code_type: Callable[..., Dict[str, Any]]) -> Callable[[str, str], Dict[str, Any]]:
    def _create_code(term: str = "Test Code", description: str = "This is a test code") -> Dict[str, Any]:
        project = create_project()
        code_type = create_code_type()
        response = client.post(
            "/codes/",
            json={
                "term": term,
                "description": description,
                "type_id": code_type["type_id"],
                "reference": "Test reference",
                "coordinates": "Test coordinates",
                "project_id": project["project_id"]
            }
        )
        assert response.status_code == 200
        return response.json()
    return _create_code

def test_create_code(create_code: Callable[..., Dict[str, Any]]) -> None:
    code = create_code()
    assert code["term"] == "Test Code"
    assert code["description"] == "This is a test code"
    assert "code_id" in code
    assert "type_id" in code
    assert "project_id" in code

def test_read_code_types(client: TestClient) -> None:
    response = client.get("/code_types/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_codes(client: TestClient) -> None:
    response = client.get("/codes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.fixture
def create_series(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> Callable[[str], Dict[str, Any]]:
    def _create_series(title: str = "Test Series") -> Dict[str, Any]:
        project = create_project()
        response = client.post(
            "/series/",
            json={"series_title": title, "project_id": project["project_id"]}
        )
        assert response.status_code == 200
        return response.json()
    return _create_series

def test_create_series(create_series: Callable[..., Dict[str, Any]]) -> None:
    series = create_series()
    assert series["series_title"] == "Test Series"
    assert "series_id" in series
    assert "project_id" in series

@pytest.fixture
def create_segment(client: TestClient, create_project: Callable[..., Dict[str, Any]], create_series: Callable[..., Dict[str, Any]]) -> Callable[[str], Dict[str, Any]]:
    def _create_segment(title: str = "Test Segment") -> Dict[str, Any]:
        project = create_project()
        series = create_series()
        response = client.post(
            "/segments/",
            json={"segment_title": title, "series_id": series["series_id"], "project_id": project["project_id"]}
        )
        assert response.status_code == 200
        return response.json()
    return _create_segment

def test_create_segment(create_segment: Callable[..., Dict[str, Any]]) -> None:
    segment = create_segment()
    assert segment["segment_title"] == "Test Segment"
    assert "segment_id" in segment
    assert "series_id" in segment
    assert "project_id" in segment

@pytest.fixture
def create_element(client: TestClient, create_project: Callable[..., Dict[str, Any]], create_segment: Callable[..., Dict[str, Any]]) -> Callable[[str], Dict[str, Any]]:
    def _create_element(text: str = "Test Element") -> Dict[str, Any]:
        project = create_project()
        segment = create_segment()
        response = client.post(
            "/elements/",
            json={"element_text": text, "segment_id": segment["segment_id"], "project_id": project["project_id"]}
        )
        assert response.status_code == 200
        return response.json()
    return _create_element

def test_create_element(create_element: Callable[..., Dict[str, Any]]) -> None:
    element = create_element()
    assert element["element_text"] == "Test Element"
    assert "element_id" in element
    assert "segment_id" in element
    assert "project_id" in element

@pytest.fixture
def create_annotation(client: TestClient, create_project: Callable[..., Dict[str, Any]], create_code: Callable[..., Dict[str, Any]], create_element: Callable[..., Dict[str, Any]]) -> Callable[[], Dict[str, Any]]:
    def _create_annotation() -> Dict[str, Any]:
        project = create_project()
        code = create_code()
        element = create_element()
        response = client.post(
            "/annotations/",
            json={"element_id": element["element_id"], "code_id": code["code_id"], "project_id": project["project_id"]}
        )
        assert response.status_code == 200
        return response.json()
    return _create_annotation

def test_create_annotation(create_annotation: Callable[..., Dict[str, Any]]) -> None:
    annotation = create_annotation()
    assert "annotation_id" in annotation
    assert "element_id" in annotation
    assert "code_id" in annotation

def test_search_elements(client: TestClient, create_element: Callable[..., Dict[str, Any]]) -> None:
    create_element("Test Element for Search")
    response = client.get("/search_elements/?search_term=Test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "element_id" in data[0]
    assert "element_text" in data[0]
    assert any("Test Element for Search" in element["element_text"] for element in data)

def test_merge_codes(client: TestClient, create_code: Callable[..., Dict[str, Any]]) -> None:
    code1 = create_code("Test Code 1", "This is a test code for merging")
    code2 = create_code("Test Code 2", "This is another test code for merging")

    response = client.post(f"/merge_codes/?code_a_id={code1['code_id']}&code_b_id={code2['code_id']}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Successfully merged Code {code1['code_id']} into Code {code2['code_id']}" in data["message"]

    # Verify that code1 no longer exists
    response = client.get(f"/codes/{code1['code_id']}")
    assert response.status_code == 404

    # Verify that code2 still exists
    response = client.get(f"/codes/{code2['code_id']}")
    assert response.status_code == 200

def test_error_handling(client: TestClient) -> None:
    # Test non-existent project
    response = client.get("/projects/9999")
    assert response.status_code == 404
    assert "detail" in response.json()

    # Test invalid input
    response = client.post("/projects/", json={"invalid_field": "Invalid data"})
    assert response.status_code == 422
    assert "detail" in response.json()

    # Test deleting non-existent project
    response = client.delete("/projects/9999")
    assert response.status_code == 404
    assert "detail" in response.json()
