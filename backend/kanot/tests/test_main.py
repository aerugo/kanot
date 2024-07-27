from typing import Any, Callable, Dict

import pytest
from fastapi.testclient import TestClient

from ..models import (
    AnnotationCreate,
    AnnotationResponse,
    AnnotationUpdate,
    BatchAnnotationCreate,
    BatchAnnotationRemove,
    CodeCreate,
    CodeResponse,
    CodeTypeCreate,
    CodeTypeResponse,
    CodeTypeUpdate,
    CodeUpdate,
    ElementCreate,
    ElementResponse,
    ElementUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    SegmentCreate,
    SegmentResponse,
    SegmentUpdate,
    SeriesCreate,
    SeriesResponse,
    SeriesUpdate,
)


@pytest.fixture
def create_project(client: TestClient) -> Callable[[str, str], Dict[str, Any]]:
    def _create_project(title: str = "Test Project", description: str = "This is a test project") -> Dict[str, Any]:
        project_create = ProjectCreate(project_title=title, project_description=description)
        response = client.post("/projects/", json=project_create.model_dump())
        assert response.status_code == 200
        return response.json()
    return _create_project

@pytest.mark.parametrize("title,description", [
    ("Test Project", "This is a test project"),
    ("Another Project", "This is another test project"),
])
def test_create_project(client: TestClient, title: str, description: str) -> None:
    project_create = ProjectCreate(project_title=title, project_description=description)
    response = client.post("/projects/", json=project_create.model_dump())
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
    response = client.put(f"/projects/{project_id}", json=project_update.model_dump())
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
    response = client.post("/projects/", json=invalid_project.model_dump())
    assert response.status_code == 422
    assert "detail" in response.json()

    # Test deleting non-existent project
    response = client.delete("/projects/9999")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_create_code_type(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    code_type_create = CodeTypeCreate(type_name="Test Code Type", project_id=project["project_id"])
    response = client.post("/code_types/", json=code_type_create.model_dump())
    assert response.status_code == 200
    data = CodeTypeResponse(**response.json())
    assert data.type_name == "Test Code Type"
    assert data.project_id == project["project_id"]

def test_update_code_type(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    code_type_create = CodeTypeCreate(type_name="Test Code Type", project_id=project["project_id"])
    create_response = client.post("/code_types/", json=code_type_create.model_dump())
    assert create_response.status_code == 200
    created_code_type = CodeTypeResponse(**create_response.json())
    
    updated_type_name = "Updated Code Type"
    code_type_update = CodeTypeUpdate(type_name=updated_type_name)
    update_response = client.put(f"/code_types/{created_code_type.type_id}", json=code_type_update.model_dump())
    assert update_response.status_code == 200
    updated_code_type = CodeTypeResponse(**update_response.json())
    assert updated_code_type.type_name == updated_type_name
    assert updated_code_type.type_id == created_code_type.type_id
    assert updated_code_type.project_id == created_code_type.project_id

def test_read_code_types(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    code_type_create = CodeTypeCreate(type_name="Test Code Type", project_id=project["project_id"])
    client.post("/code_types/", json=code_type_create.model_dump())
    response = client.get("/code_types/")
    assert response.status_code == 200
    data = [CodeTypeResponse(**item) for item in response.json()]
    assert len(data) > 0
    assert any(ct.type_name == "Test Code Type" for ct in data)

def test_create_code(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    code_type_create = CodeTypeCreate(type_name="Test Code Type", project_id=project["project_id"])
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    code_type_id = code_type_response.json()["type_id"]
    
    code_create = CodeCreate(
        term="Test Code",
        description="Test Description",
        type_id=code_type_id,
        reference="Test Reference",
        coordinates="Test Coordinates",
        project_id=project["project_id"]
    )
    response = client.post("/codes/", json=code_create.model_dump())
    assert response.status_code == 200
    data = CodeResponse(**response.json())
    assert data.term == "Test Code"
    assert data.description == "Test Description"
    assert data.type_id == code_type_id
    assert data.project_id == project["project_id"]

def test_read_codes(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    code_type_create = CodeTypeCreate(type_name="Test Code Type", project_id=project["project_id"])
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    code_type_id = code_type_response.json()["type_id"]
    
    code_create = CodeCreate(
        term="Test Code",
        description="Test Description",
        type_id=code_type_id,
        reference="Test Reference",
        coordinates="Test Coordinates",
        project_id=project["project_id"]
    )
    client.post("/codes/", json=code_create.model_dump())
    response = client.get("/codes/")
    assert response.status_code == 200
    data = [CodeResponse(**item) for item in response.json()]
    assert len(data) > 0
    assert any(c.term == "Test Code" for c in data)

def test_update_code(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    code_type_create = CodeTypeCreate(type_name="Test Code Type", project_id=project["project_id"])
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    code_type_id = code_type_response.json()["type_id"]
    
    code_create = CodeCreate(
        term="Test Code",
        description="Test Description",
        type_id=code_type_id,
        reference="Test Reference",
        coordinates="Test Coordinates",
        project_id=project["project_id"]
    )
    create_response = client.post("/codes/", json=code_create.model_dump())
    assert create_response.status_code == 200
    created_code = CodeResponse(**create_response.json())
    
    updated_term = "Updated Code"
    updated_description = "Updated Description"
    code_update = CodeUpdate(
        term=updated_term,
        description=updated_description,
        type_id=code_type_id,
        reference="Updated Reference",
        coordinates="Updated Coordinates"
    )
    update_response = client.put(f"/codes/{created_code.code_id}", json=code_update.model_dump())
    assert update_response.status_code == 200
    updated_code = CodeResponse(**update_response.json())
    assert updated_code.term == updated_term
    assert updated_code.description == updated_description
    assert updated_code.reference == "Updated Reference"
    assert updated_code.coordinates == "Updated Coordinates"
    assert updated_code.code_id == created_code.code_id
    assert updated_code.type_id == code_type_id
    assert updated_code.project_id == project["project_id"]

def test_create_series(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    response = client.post("/series/", json=series_create.model_dump())
    assert response.status_code == 200
    data = SeriesResponse(**response.json())
    assert data.series_title == "Test Series"
    assert data.project_id == project["project_id"]

def test_read_series(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    client.post("/series/", json=series_create.model_dump())
    response = client.get("/series/")
    assert response.status_code == 200
    data = [SeriesResponse(**item) for item in response.json()]
    assert len(data) > 0
    assert any(s.series_title == "Test Series" for s in data)

def test_update_series(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    create_response = client.post("/series/", json=series_create.model_dump())
    assert create_response.status_code == 200
    created_series = SeriesResponse(**create_response.json())
    
    updated_title = "Updated Series"
    series_update = SeriesUpdate(series_title=updated_title)
    update_response = client.put(f"/series/{created_series.series_id}", json=series_update.model_dump())
    assert update_response.status_code == 200
    updated_series = SeriesResponse(**update_response.json())
    assert updated_series.series_title == updated_title
    assert updated_series.series_id == created_series.series_id
    assert updated_series.project_id == created_series.project_id

def test_create_segment(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    series_response = client.post("/series/", json=series_create.model_dump())
    series_id = series_response.json()["series_id"]
    
    segment_create = SegmentCreate(segment_title="Test Segment", series_id=series_id, project_id=project["project_id"])
    response = client.post("/segments/", json=segment_create.model_dump())
    assert response.status_code == 200
    data = SegmentResponse(**response.json())
    assert data.segment_title == "Test Segment"
    assert data.series_id == series_id
    assert data.project_id == project["project_id"]

def test_read_segments(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    series_response = client.post("/series/", json=series_create.model_dump())
    series_id = series_response.json()["series_id"]
    
    segment_create = SegmentCreate(segment_title="Test Segment", series_id=series_id, project_id=project["project_id"])
    client.post("/segments/", json=segment_create.model_dump())
    response = client.get("/segments/")
    assert response.status_code == 200
    data = [SegmentResponse(**item) for item in response.json()]
    assert len(data) > 0
    assert any(s.segment_title == "Test Segment" for s in data)

def test_create_element(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    series_response = client.post("/series/", json=series_create.model_dump())
    series_id = series_response.json()["series_id"]
    
    segment_create = SegmentCreate(segment_title="Test Segment", series_id=series_id, project_id=project["project_id"])
    segment_response = client.post("/segments/", json=segment_create.model_dump())
    segment_id = segment_response.json()["segment_id"]
    
    element_create = ElementCreate(element_text="Test Element", segment_id=segment_id, project_id=project["project_id"])
    response = client.post("/elements/", json=element_create.model_dump())
    assert response.status_code == 200
    data = ElementResponse(**response.json())
    assert data.element_text == "Test Element"
    assert data.segment_id == segment_id
    assert data.project_id == project["project_id"]

def test_read_elements(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    series_response = client.post("/series/", json=series_create.model_dump())
    series_id = series_response.json()["series_id"]
    
    segment_create = SegmentCreate(segment_title="Test Segment", series_id=series_id, project_id=project["project_id"])
    segment_response = client.post("/segments/", json=segment_create.model_dump())
    segment_id = segment_response.json()["segment_id"]
    
    element_create = ElementCreate(element_text="Test Element", segment_id=segment_id, project_id=project["project_id"])
    client.post("/elements/", json=element_create.model_dump())
    response = client.get("/elements/")
    assert response.status_code == 200
    data = [ElementResponse(**item) for item in response.json()]
    assert len(data) > 0
    assert any(e.element_text == "Test Element" for e in data)

def test_create_annotation(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    
    # Create code type and code
    code_type_create = CodeTypeCreate(type_name="Test Code Type", project_id=project["project_id"])
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    code_type_id = code_type_response.json()["type_id"]
    
    code_create = CodeCreate(
        term="Test Code",
        description="Test Description",
        type_id=code_type_id,
        reference="Test Reference",
        coordinates="Test Coordinates",
        project_id=project["project_id"]
    )
    code_response = client.post("/codes/", json=code_create.model_dump())
    code_id = code_response.json()["code_id"]
    
    # Create series, segment, and element
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    series_response = client.post("/series/", json=series_create.model_dump())
    series_id = series_response.json()["series_id"]
    
    segment_create = SegmentCreate(segment_title="Test Segment", series_id=series_id, project_id=project["project_id"])
    segment_response = client.post("/segments/", json=segment_create.model_dump())
    segment_id = segment_response.json()["segment_id"]
    
    element_create = ElementCreate(element_text="Test Element", segment_id=segment_id, project_id=project["project_id"])
    element_response = client.post("/elements/", json=element_create.model_dump())
    element_id = element_response.json()["id"]
    
    # Create annotation
    annotation_create = AnnotationCreate(element_id=element_id, code_id=code_id, project_id=project["project_id"])
    response = client.post("/annotations/", json=annotation_create.model_dump())
    assert response.status_code == 200
    data = AnnotationResponse(**response.json())
    assert data.element_id == element_id
    assert data.code_id == code_id
    assert data.project_id == project["project_id"]

def test_read_annotations(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    
    # Create code type and code
    code_type_create = CodeTypeCreate(type_name="Test Code Type", project_id=project["project_id"])
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    code_type_id = code_type_response.json()["type_id"]
    
    code_create = CodeCreate(
        term="Test Code",
        description="Test Description",
        type_id=code_type_id,
        reference="Test Reference",
        coordinates="Test Coordinates",
        project_id=project["project_id"]
    )
    code_response = client.post("/codes/", json=code_create.model_dump())
    code_id = code_response.json()["code_id"]
    
    # Create series, segment, and element
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    series_response = client.post("/series/", json=series_create.model_dump())
    series_id = series_response.json()["series_id"]
    
    segment_create = SegmentCreate(segment_title="Test Segment", series_id=series_id, project_id=project["project_id"])
    segment_response = client.post("/segments/", json=segment_create.model_dump())
    segment_id = segment_response.json()["segment_id"]
    
    element_create = ElementCreate(element_text="Test Element", segment_id=segment_id, project_id=project["project_id"])
    element_response = client.post("/elements/", json=element_create.model_dump())
    element_id = element_response.json()["id"]
    
    # Create annotation
    annotation_create = AnnotationCreate(element_id=element_id, code_id=code_id, project_id=project["project_id"])
    client.post("/annotations/", json=annotation_create.model_dump())
    
    response = client.get("/annotations/")
    assert response.status_code == 200
    data = [AnnotationResponse(**item) for item in response.json()]
    assert len(data) > 0
    assert any(a.element_id == element_id and a.code_id == code_id for a in data)

def test_update_annotation(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    
    # Create code type and code
    code_type_create = CodeTypeCreate(type_name="Test Code Type", project_id=project["project_id"])
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    code_type_id = code_type_response.json()["type_id"]
    
    code_create = CodeCreate(
        term="Test Code",
        description="Test Description",
        type_id=code_type_id,
        reference="Test Reference",
        coordinates="Test Coordinates",
        project_id=project["project_id"]
    )
    code_response = client.post("/codes/", json=code_create.model_dump())
    code_id = code_response.json()["code_id"]
    
    # Create another code for updating
    another_code_create = CodeCreate(
        term="Another Code",
        description="Another Description",
        type_id=code_type_id,
        reference="Another Reference",
        coordinates="Another Coordinates",
        project_id=project["project_id"]
    )
    another_code_response = client.post("/codes/", json=another_code_create.model_dump())
    another_code_id = another_code_response.json()["code_id"]
    
    # Create series, segment, and element
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    series_response = client.post("/series/", json=series_create.model_dump())
    series_id = series_response.json()["series_id"]
    
    segment_create = SegmentCreate(segment_title="Test Segment", series_id=series_id, project_id=project["project_id"])
    segment_response = client.post("/segments/", json=segment_create.model_dump())
    segment_id = segment_response.json()["segment_id"]
    
    element_create = ElementCreate(element_text="Test Element", segment_id=segment_id, project_id=project["project_id"])
    element_response = client.post("/elements/", json=element_create.model_dump())
    element_id = element_response.json()["id"]
    
    # Create annotation
    annotation_create = AnnotationCreate(element_id=element_id, code_id=code_id, project_id=project["project_id"])
    annotation_response = client.post("/annotations/", json=annotation_create.model_dump())
    annotation_id = annotation_response.json()["id"]
    
    # Update annotation
    annotation_update = AnnotationUpdate(element_id=element_id, code_id=another_code_id)
    response = client.put(f"/annotations/{annotation_id}", json=annotation_update.model_dump())
    
    assert response.status_code == 200
    updated_annotation = AnnotationResponse(**response.json())
    assert updated_annotation.element_id == element_id
    assert updated_annotation.code_id == another_code_id
    assert updated_annotation.code.term == "Another Code"

def test_merge_codes(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    
    # Create code type
    code_type_create = CodeTypeCreate(type_name="Test Code Type", project_id=project["project_id"])
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    code_type_id = code_type_response.json()["type_id"]
    
    # Create two codes
    code_create_1 = CodeCreate(
        term="Test Code 1",
        description="Test Description 1",
        type_id=code_type_id,
        reference="Test Reference 1",
        coordinates="Test Coordinates 1",
        project_id=project["project_id"]
    )
    code_response_1 = client.post("/codes/", json=code_create_1.model_dump())
    code_id_1 = code_response_1.json()["code_id"]
    
    code_create_2 =CodeCreate(
        term="Test Code 2",
        description="Test Description 2",
        type_id=code_type_id,
        reference="Test Reference 2",
        coordinates="Test Coordinates 2",
        project_id=project["project_id"]
    )
    code_response_2 = client.post("/codes/", json=code_create_2.model_dump())
    code_id_2 = code_response_2.json()["code_id"]
    
    # Merge codes
    response = client.post(f"/merge_codes/?code_a_id={code_id_1}&code_b_id={code_id_2}")
    assert response.status_code == 200
    assert "Successfully merged" in response.json()["message"]
    
    # Check that code_id_1 no longer exists
    response = client.get(f"/codes/{code_id_1}")
    assert response.status_code == 404
    
    # Check that code_id_2 still exists
    response = client.get(f"/codes/{code_id_2}")
    assert response.status_code == 200

def test_search_elements(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    
    # Create series, segment, and elements
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    series_response = client.post("/series/", json=series_create.model_dump())
    series_id = series_response.json()["series_id"]
    
    segment_create = SegmentCreate(segment_title="Test Segment", series_id=series_id, project_id=project["project_id"])
    segment_response = client.post("/segments/", json=segment_create.model_dump())
    segment_id = segment_response.json()["segment_id"]
    
    element_create_1 = ElementCreate(element_text="Test Element 1", segment_id=segment_id, project_id=project["project_id"])
    client.post("/elements/", json=element_create_1.model_dump())
    
    element_create_2 = ElementCreate(element_text="Another Element", segment_id=segment_id, project_id=project["project_id"])
    client.post("/elements/", json=element_create_2.model_dump())
    
    # Search for elements
    response = client.get("/search_elements/?search_term=Test")
    assert response.status_code == 200
    data = [ElementResponse(**item) for item in response.json()]
    assert len(data) == 1
    assert data[0].element_text == "Test Element 1"
    
    # Check pagination headers
    assert "X-Total-Count" in response.headers
    assert "X-Limit" in response.headers
    assert "X-Skip" in response.headers

def test_remove_batch_annotations(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    
    # Create code type and codes
    code_type_create = CodeTypeCreate(type_name="Test Code Type", project_id=project["project_id"])
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    assert code_type_response.status_code == 200
    code_type_id = code_type_response.json()["type_id"]
    
    code_create_1 = CodeCreate(term="Code 1", description="Description 1", type_id=code_type_id, project_id=project["project_id"])
    code_create_2 = CodeCreate(term="Code 2", description="Description 2", type_id=code_type_id, project_id=project["project_id"])
    code_response_1 = client.post("/codes/", json=code_create_1.model_dump())
    code_response_2 = client.post("/codes/", json=code_create_2.model_dump())
    assert code_response_1.status_code == 200 and code_response_2.status_code == 200
    code_id_1 = code_response_1.json()["code_id"]
    code_id_2 = code_response_2.json()["code_id"]
    
    # Create a series, segment, and elements
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    series_response = client.post("/series/", json=series_create.model_dump())
    assert series_response.status_code == 200
    series_id = series_response.json()["series_id"]
    
    segment_create = SegmentCreate(segment_title="Test Segment", series_id=series_id, project_id=project["project_id"])
    segment_response = client.post("/segments/", json=segment_create.model_dump())
    assert segment_response.status_code == 200
    segment_id = segment_response.json()["segment_id"]
    
    element_create_1 = ElementCreate(element_text="Element 1", segment_id=segment_id, project_id=project["project_id"])
    element_create_2 = ElementCreate(element_text="Element 2", segment_id=segment_id, project_id=project["project_id"])
    element_response_1 = client.post("/elements/", json=element_create_1.model_dump())
    element_response_2 = client.post("/elements/", json=element_create_2.model_dump())
    assert element_response_1.status_code == 200 and element_response_2.status_code == 200
    element_id_1 = element_response_1.json()["element_id"]
    element_id_2 = element_response_2.json()["element_id"]
    
    # Create batch annotations
    batch_annotation_create = BatchAnnotationCreate(
        element_ids=[element_id_1, element_id_2],
        code_ids=[code_id_1, code_id_2],
        project_id=project["project_id"]
    )
    response = client.post("/batch_annotations/", json=batch_annotation_create.model_dump())
    assert response.status_code == 200
    created_annotations = response.json()
    assert len(created_annotations) == 4  # 2 elements * 2 codes = 4 annotations

def test_read_codes_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a code type
    code_type_create = CodeTypeCreate(type_name="Test Type", project_id=project_id)
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    assert code_type_response.status_code == 200
    code_type_id = code_type_response.json()["type_id"]

    # Create some codes
    code1 = client.post("/codes/", json={"term": "Code 1", "description": "Description 1", "type_id": code_type_id, "project_id": project_id})
    code2 = client.post("/codes/", json={"term": "Code 2", "description": "Description 2", "type_id": code_type_id, "project_id": project_id})
    
    assert code1.status_code == 200
    assert code2.status_code == 200

    # Read codes for the project
    response = client.get(f"/codes/?project_id={project_id}")
    assert response.status_code == 200
    codes = response.json()
    assert isinstance(codes, list)
    assert len(codes) == 2
    assert any(code["term"] == "Code 1" for code in codes)
    assert any(code["term"] == "Code 2" for code in codes)
    assert all(code["project_id"] == project_id for code in codes)

def test_read_series_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create some series
    series1 = client.post("/series/", json={"series_title": "Series 1", "project_id": project_id})
    series2 = client.post("/series/", json={"series_title": "Series 2", "project_id": project_id})
    
    assert series1.status_code == 200
    assert series2.status_code == 200

    # Read series for the project
    response = client.get(f"/series/?project_id={project_id}")
    assert response.status_code == 200
    series_list = response.json()
    assert isinstance(series_list, list)
    assert len(series_list) == 2
    assert any(series["series_title"] == "Series 1" for series in series_list)
    assert any(series["series_title"] == "Series 2" for series in series_list)
    assert all(series["project_id"] == project_id for series in series_list)

def test_read_segments_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a series
    series_response = client.post("/series/", json={"series_title": "Test Series", "project_id": project_id})
    assert series_response.status_code == 200
    series_id = series_response.json()["series_id"]

    # Create some segments
    segment1 = client.post("/segments/", json={"segment_title": "Segment 1", "series_id": series_id, "project_id": project_id})
    segment2 = client.post("/segments/", json={"segment_title": "Segment 2", "series_id": series_id, "project_id": project_id})
    
    assert segment1.status_code == 200
    assert segment2.status_code == 200

    # Read segments for the project
    response = client.get(f"/segments/?project_id={project_id}")
    assert response.status_code == 200
    segments = response.json()
    assert isinstance(segments, list)
    assert len(segments) == 2
    assert any(segment["segment_title"] == "Segment 1" for segment in segments)
    assert any(segment["segment_title"] == "Segment 2" for segment in segments)
    assert all(segment["project_id"] == project_id for segment in segments)

def test_read_codes_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a code type
    code_type_create = CodeTypeCreate(type_name="Test Type", project_id=project_id)
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    assert code_type_response.status_code == 200
    code_type_id = code_type_response.json()["type_id"]

    # Create some codes
    code1 = client.post("/codes/", json={"term": "Code 1", "description": "Description 1", "type_id": code_type_id, "project_id": project_id})
    code2 = client.post("/codes/", json={"term": "Code 2", "description": "Description 2", "type_id": code_type_id, "project_id": project_id})
    
    assert code1.status_code == 200
    assert code2.status_code == 200

    # Read codes for the project
    response = client.get(f"/codes/?project_id={project_id}")
    assert response.status_code == 200
    codes = response.json()
    assert isinstance(codes, list)
    assert len(codes) == 2
    assert any(code["term"] == "Code 1" for code in codes)
    assert any(code["term"] == "Code 2" for code in codes)
    assert all(code["project_id"] == project_id for code in codes)

def test_read_series_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create some series
    series1 = client.post("/series/", json={"series_title": "Series 1", "project_id": project_id})
    series2 = client.post("/series/", json={"series_title": "Series 2", "project_id": project_id})
    
    assert series1.status_code == 200
    assert series2.status_code == 200

    # Read series for the project
    response = client.get(f"/series/?project_id={project_id}")
    assert response.status_code == 200
    series_list = response.json()
    assert isinstance(series_list, list)
    assert len(series_list) == 2
    assert any(series["series_title"] == "Series 1" for series in series_list)
    assert any(series["series_title"] == "Series 2" for series in series_list)
    assert all(series["project_id"] == project_id for series in series_list)

def test_read_segments_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a series
    series_response = client.post("/series/", json={"series_title": "Test Series", "project_id": project_id})
    assert series_response.status_code == 200
    series_id = series_response.json()["series_id"]

    # Create some segments
    segment1 = client.post("/segments/", json={"segment_title": "Segment 1", "series_id": series_id, "project_id": project_id})
    segment2 = client.post("/segments/", json={"segment_title": "Segment 2", "series_id": series_id, "project_id": project_id})
    
    assert segment1.status_code == 200
    assert segment2.status_code == 200

    # Read segments for the project
    response = client.get(f"/segments/?project_id={project_id}")
    assert response.status_code == 200
    segments = response.json()
    assert isinstance(segments, list)
    assert len(segments) == 2
    assert any(segment["segment_title"] == "Segment 1" for segment in segments)
    assert any(segment["segment_title"] == "Segment 2" for segment in segments)
    assert all(segment["project_id"] == project_id for segment in segments)

def test_read_codes_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a code type
    code_type_create = CodeTypeCreate(type_name="Test Type", project_id=project_id)
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    assert code_type_response.status_code == 200
    code_type_id = code_type_response.json()["type_id"]

    # Create some codes
    code1 = client.post("/codes/", json={"term": "Code 1", "description": "Description 1", "type_id": code_type_id, "project_id": project_id})
    code2 = client.post("/codes/", json={"term": "Code 2", "description": "Description 2", "type_id": code_type_id, "project_id": project_id})
    
    assert code1.status_code == 200
    assert code2.status_code == 200

    # Read codes for the project
    response = client.get(f"/codes/?project_id={project_id}")
    assert response.status_code == 200
    codes = response.json()
    assert isinstance(codes, list)
    assert len(codes) == 2
    assert any(code["term"] == "Code 1" for code in codes)
    assert any(code["term"] == "Code 2" for code in codes)
    assert all(code["project_id"] == project_id for code in codes)

def test_read_series_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create some series
    series1 = client.post("/series/", json={"series_title": "Series 1", "project_id": project_id})
    series2 = client.post("/series/", json={"series_title": "Series 2", "project_id": project_id})
    
    assert series1.status_code == 200
    assert series2.status_code == 200

    # Read series for the project
    response = client.get(f"/series/?project_id={project_id}")
    assert response.status_code == 200
    series_list = response.json()
    assert isinstance(series_list, list)
    assert len(series_list) == 2
    assert any(series["series_title"] == "Series 1" for series in series_list)
    assert any(series["series_title"] == "Series 2" for series in series_list)
    assert all(series["project_id"] == project_id for series in series_list)

def test_read_segments_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a series
    series_response = client.post("/series/", json={"series_title": "Test Series", "project_id": project_id})
    assert series_response.status_code == 200
    series_id = series_response.json()["series_id"]

    # Create some segments
    segment1 = client.post("/segments/", json={"segment_title": "Segment 1", "series_id": series_id, "project_id": project_id})
    segment2 = client.post("/segments/", json={"segment_title": "Segment 2", "series_id": series_id, "project_id": project_id})
    
    assert segment1.status_code == 200
    assert segment2.status_code == 200

    # Read segments for the project
    response = client.get(f"/segments/?project_id={project_id}")
    assert response.status_code == 200
    segments = response.json()
    assert isinstance(segments, list)
    assert len(segments) == 2
    assert any(segment["segment_title"] == "Segment 1" for segment in segments)
    assert any(segment["segment_title"] == "Segment 2" for segment in segments)
    assert all(segment["project_id"] == project_id for segment in segments)

def test_read_codes_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a code type
    code_type_create = CodeTypeCreate(type_name="Test Type", project_id=project_id)
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    assert code_type_response.status_code == 200
    code_type_id = code_type_response.json()["type_id"]

    # Create some codes
    code1 = client.post("/codes/", json={"term": "Code 1", "description": "Description 1", "type_id": code_type_id, "project_id": project_id})
    code2 = client.post("/codes/", json={"term": "Code 2", "description": "Description 2", "type_id": code_type_id, "project_id": project_id})
    
    assert code1.status_code == 200
    assert code2.status_code == 200

    # Read codes for the project
    response = client.get(f"/codes/?project_id={project_id}")
    assert response.status_code == 200
    codes = response.json()
    assert isinstance(codes, list)
    assert len(codes) == 2
    assert any(code["term"] == "Code 1" for code in codes)
    assert any(code["term"] == "Code 2" for code in codes)
    assert all(code["project_id"] == project_id for code in codes)

def test_read_series_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create some series
    series1 = client.post("/series/", json={"series_title": "Series 1", "project_id": project_id})
    series2 = client.post("/series/", json={"series_title": "Series 2", "project_id": project_id})
    
    assert series1.status_code == 200
    assert series2.status_code == 200

    # Read series for the project
    response = client.get(f"/series/?project_id={project_id}")
    assert response.status_code == 200
    series_list = response.json()
    assert isinstance(series_list, list)
    assert len(series_list) == 2
    assert any(series["series_title"] == "Series 1" for series in series_list)
    assert any(series["series_title"] == "Series 2" for series in series_list)
    assert all(series["project_id"] == project_id for series in series_list)

def test_read_segments_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a series
    series_response = client.post("/series/", json={"series_title": "Test Series", "project_id": project_id})
    assert series_response.status_code == 200
    series_id = series_response.json()["series_id"]

    # Create some segments
    segment1 = client.post("/segments/", json={"segment_title": "Segment 1", "series_id": series_id, "project_id": project_id})
    segment2 = client.post("/segments/", json={"segment_title": "Segment 2", "series_id": series_id, "project_id": project_id})
    
    assert segment1.status_code == 200
    assert segment2.status_code == 200

    # Read segments for the project
    response = client.get(f"/segments/?project_id={project_id}")
    assert response.status_code == 200
    segments = response.json()
    assert isinstance(segments, list)
    assert len(segments) == 2
    assert any(segment["segment_title"] == "Segment 1" for segment in segments)
    assert any(segment["segment_title"] == "Segment 2" for segment in segments)
    assert all(segment["project_id"] == project_id for segment in segments)

def test_read_codes_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a code type
    code_type_create = CodeTypeCreate(type_name="Test Type", project_id=project_id)
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    assert code_type_response.status_code == 200
    code_type_id = code_type_response.json()["type_id"]

    # Create some codes
    code1 = client.post("/codes/", json={"term": "Code 1", "description": "Description 1", "type_id": code_type_id, "project_id": project_id})
    code2 = client.post("/codes/", json={"term": "Code 2", "description": "Description 2", "type_id": code_type_id, "project_id": project_id})
    
    assert code1.status_code == 200
    assert code2.status_code == 200

    # Read codes for the project
    response = client.get(f"/codes/?project_id={project_id}")
    assert response.status_code == 200
    codes = response.json()
    assert isinstance(codes, list)
    assert len(codes) == 2
    assert any(code["term"] == "Code 1" for code in codes)
    assert any(code["term"] == "Code 2" for code in codes)
    assert all(code["project_id"] == project_id for code in codes)

def test_read_series_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create some series
    series1 = client.post("/series/", json={"series_title": "Series 1", "project_id": project_id})
    series2 = client.post("/series/", json={"series_title": "Series 2", "project_id": project_id})
    
    assert series1.status_code == 200
    assert series2.status_code == 200

    # Read series for the project
    response = client.get(f"/series/?project_id={project_id}")
    assert response.status_code == 200
    series_list = response.json()
    assert isinstance(series_list, list)
    assert len(series_list) == 2
    assert any(series["series_title"] == "Series 1" for series in series_list)
    assert any(series["series_title"] == "Series 2" for series in series_list)
    assert all(series["project_id"] == project_id for series in series_list)

def test_read_segments_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a series
    series_response = client.post("/series/", json={"series_title": "Test Series", "project_id": project_id})
    assert series_response.status_code == 200
    series_id = series_response.json()["series_id"]

    # Create some segments
    segment1 = client.post("/segments/", json={"segment_title": "Segment 1", "series_id": series_id, "project_id": project_id})
    segment2 = client.post("/segments/", json={"segment_title": "Segment 2", "series_id": series_id, "project_id": project_id})
    
    assert segment1.status_code == 200
    assert segment2.status_code == 200

    # Read segments for the project
    response = client.get(f"/segments/?project_id={project_id}")
    assert response.status_code == 200
    segments = response.json()
    assert isinstance(segments, list)
    assert len(segments) == 2
    assert any(segment["segment_title"] == "Segment 1" for segment in segments)
    assert any(segment["segment_title"] == "Segment 2" for segment in segments)
    assert all(segment["project_id"] == project_id for segment in segments)

def test_read_codes_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a code type
    code_type_create = CodeTypeCreate(type_name="Test Type", project_id=project_id)
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    assert code_type_response.status_code == 200
    code_type_id = code_type_response.json()["type_id"]

    # Create some codes
    code1 = client.post("/codes/", json={"term": "Code 1", "description": "Description 1", "type_id": code_type_id, "project_id": project_id})
    code2 = client.post("/codes/", json={"term": "Code 2", "description": "Description 2", "type_id": code_type_id, "project_id": project_id})
    
    assert code1.status_code == 200
    assert code2.status_code == 200

    # Read codes for the project
    response = client.get(f"/codes/?project_id={project_id}")
    assert response.status_code == 200
    codes = response.json()
    assert isinstance(codes, list)
    assert len(codes) == 2
    assert any(code["term"] == "Code 1" for code in codes)
    assert any(code["term"] == "Code 2" for code in codes)
    assert all(code["project_id"] == project_id for code in codes)

def test_read_series_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create some series
    series1 = client.post("/series/", json={"series_title": "Series 1", "project_id": project_id})
    series2 = client.post("/series/", json={"series_title": "Series 2", "project_id": project_id})
    
    assert series1.status_code == 200
    assert series2.status_code == 200

    # Read series for the project
    response = client.get(f"/series/?project_id={project_id}")
    assert response.status_code == 200
    series_list = response.json()
    assert isinstance(series_list, list)
    assert len(series_list) == 2
    assert any(series["series_title"] == "Series 1" for series in series_list)
    assert any(series["series_title"] == "Series 2" for series in series_list)
    assert all(series["project_id"] == project_id for series in series_list)

def test_read_segments_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a series
    series_response = client.post("/series/", json={"series_title": "Test Series", "project_id": project_id})
    assert series_response.status_code == 200
    series_id = series_response.json()["series_id"]

    # Create some segments
    segment1 = client.post("/segments/", json={"segment_title": "Segment 1", "series_id": series_id, "project_id": project_id})
    segment2 = client.post("/segments/", json={"segment_title": "Segment 2", "series_id": series_id, "project_id": project_id})
    
    assert segment1.status_code == 200
    assert segment2.status_code == 200

    # Read segments for the project
    response = client.get(f"/segments/?project_id={project_id}")
    assert response.status_code == 200
    segments = response.json()
    assert isinstance(segments, list)
    assert len(segments) == 2
    assert any(segment["segment_title"] == "Segment 1" for segment in segments)
    assert any(segment["segment_title"] == "Segment 2" for segment in segments)
    assert all(segment["project_id"] == project_id for segment in segments)

def test_read_codes_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a code type
    code_type_create = CodeTypeCreate(type_name="Test Type", project_id=project_id)
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    assert code_type_response.status_code == 200
    code_type_id = code_type_response.json()["type_id"]

    # Create some codes
    code1 = client.post("/codes/", json={"term": "Code 1", "description": "Description 1", "type_id": code_type_id, "project_id": project_id})
    code2 = client.post("/codes/", json={"term": "Code 2", "description": "Description 2", "type_id": code_type_id, "project_id": project_id})
    
    assert code1.status_code == 200
    assert code2.status_code == 200

    # Read codes for the project
    response = client.get(f"/codes/?project_id={project_id}")
    assert response.status_code == 200
    codes = response.json()
    assert isinstance(codes, list)
    assert len(codes) == 2
    assert any(code["term"] == "Code 1" for code in codes)
    assert any(code["term"] == "Code 2" for code in codes)
    assert all(code["project_id"] == project_id for code in codes)

def test_read_series_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create some series
    series1 = client.post("/series/", json={"series_title": "Series 1", "project_id": project_id})
    series2 = client.post("/series/", json={"series_title": "Series 2", "project_id": project_id})
    
    assert series1.status_code == 200
    assert series2.status_code == 200

    # Read series for the project
    response = client.get(f"/series/?project_id={project_id}")
    assert response.status_code == 200
    series_list = response.json()
    assert isinstance(series_list, list)
    assert len(series_list) == 2
    assert any(series["series_title"] == "Series 1" for series in series_list)
    assert any(series["series_title"] == "Series 2" for series in series_list)
    assert all(series["project_id"] == project_id for series in series_list)

def test_read_segments_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a series
    series_response = client.post("/series/", json={"series_title": "Test Series", "project_id": project_id})
    assert series_response.status_code == 200
    series_id = series_response.json()["series_id"]

    # Create some segments
    segment1 = client.post("/segments/", json={"segment_title": "Segment 1", "series_id": series_id, "project_id": project_id})
    segment2 = client.post("/segments/", json={"segment_title": "Segment 2", "series_id": series_id, "project_id": project_id})
    
    assert segment1.status_code == 200
    assert segment2.status_code == 200

    # Read segments for the project
    response = client.get(f"/segments/?project_id={project_id}")
    assert response.status_code == 200
    segments = response.json()
    assert isinstance(segments, list)
    assert len(segments) == 2
    assert any(segment["segment_title"] == "Segment 1" for segment in segments)
    assert any(segment["segment_title"] == "Segment 2" for segment in segments)
    assert all(segment["project_id"] == project_id for segment in segments)
    response = client.post("/batch_annotations/", json=batch_annotation_create.model_dump())
    assert response.status_code == 200
    created_annotations = response.json()
    assert len(created_annotations) == 4  # 2 elements * 2 codes = 4 annotations

def test_read_codes_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a code type
    code_type_create = CodeTypeCreate(type_name="Test Type", project_id=project_id)
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    assert code_type_response.status_code == 200
    code_type_id = code_type_response.json()["type_id"]

    # Create some codes
    code1 = client.post("/codes/", json={"term": "Code 1", "description": "Description 1", "type_id": code_type_id, "project_id": project_id})
    code2 = client.post("/codes/", json={"term": "Code 2", "description": "Description 2", "type_id": code_type_id, "project_id": project_id})
    
    assert code1.status_code == 200
    assert code2.status_code == 200

    # Read codes for the project
    response = client.get(f"/codes/?project_id={project_id}")
    assert response.status_code == 200
    codes = response.json()
    assert isinstance(codes, list)
    assert len(codes) == 2
    assert any(code["term"] == "Code 1" for code in codes)
    assert any(code["term"] == "Code 2" for code in codes)
    assert all(code["project_id"] == project_id for code in codes)

def test_read_series_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create some series
    series1 = client.post("/series/", json={"series_title": "Series 1", "project_id": project_id})
    series2 = client.post("/series/", json={"series_title": "Series 2", "project_id": project_id})
    
    assert series1.status_code == 200
    assert series2.status_code == 200

    # Read series for the project
    response = client.get(f"/series/?project_id={project_id}")
    assert response.status_code == 200
    series_list = response.json()
    assert isinstance(series_list, list)
    assert len(series_list) == 2
    assert any(series["series_title"] == "Series 1" for series in series_list)
    assert any(series["series_title"] == "Series 2" for series in series_list)
    assert all(series["project_id"] == project_id for series in series_list)

def test_read_segments_by_project(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    project_id = project["project_id"]

    # Create a series
    series_response = client.post("/series/", json={"series_title": "Test Series", "project_id": project_id})
    assert series_response.status_code == 200
    series_id = series_response.json()["series_id"]

    # Create some segments
    segment1 = client.post("/segments/", json={"segment_title": "Segment 1", "series_id": series_id, "project_id": project_id})
    segment2 = client.post("/segments/", json={"segment_title": "Segment 2", "series_id": series_id, "project_id": project_id})
    
    assert segment1.status_code == 200
    assert segment2.status_code == 200

    # Read segments for the project
    response = client.get(f"/segments/?project_id={project_id}")
    assert response.status_code == 200
    segments = response.json()
    assert isinstance(segments, list)
    assert len(segments) == 2
    assert any(segment["segment_title"] == "Segment 1" for segment in segments)
    assert any(segment["segment_title"] == "Segment 2" for segment in segments)
    assert all(segment["project_id"] == project_id for segment in segments)
    
    from urllib.parse import urlencode

    # Remove batch annotations
    batch_annotation_remove = BatchAnnotationRemove(
        element_ids=[element_id_1],
        code_ids=[code_id_1]
    )
    query_params = urlencode(batch_annotation_remove.model_dump(by_alias=True), doseq=True)
    response = client.delete(f"/batch_annotations/?{query_params}")
    
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}. Response: {response.text}"
    removed_annotations = response.json()
    assert len(removed_annotations) == 1  # 1 element * 1 code = 1 annotation removed
    
    # Verify the remaining annotations
    response = client.get("/annotations/")
    assert response.status_code == 200
    remaining_annotations = response.json()
    assert len(remaining_annotations) == 3  # 4 original - 1 removed = 3 remaining

def test_update_element(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    
    # Create series and segment
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    series_response = client.post("/series/", json=series_create.model_dump())
    series_id = series_response.json()["series_id"]
    
    segment_create = SegmentCreate(segment_title="Test Segment", series_id=series_id, project_id=project["project_id"])
    segment_response = client.post("/segments/", json=segment_create.model_dump())
    segment_id = segment_response.json()["segment_id"]
    
    # Create an element
    element_create = ElementCreate(element_text="Initial Text", segment_id=segment_id, project_id=project["project_id"])
    element_response = client.post("/elements/", json=element_create.model_dump())
    assert element_response.status_code == 200
    element_id = element_response.json()["element_id"]

    # Update the element
    element_update = ElementUpdate(element_text="Updated Text")
    update_response = client.put(f"/elements/{element_id}", json=element_update.model_dump())
    assert update_response.status_code == 200
    updated_element = ElementResponse(**update_response.json())

    # Check if the element was updated correctly
    assert updated_element.element_id == element_id
    assert updated_element.element_text == "Updated Text"
    assert updated_element.segment_id == segment_id
    assert updated_element.project_id == project["project_id"]

    # Verify the update by getting the element
    get_response = client.get(f"/elements/{element_id}")
    assert get_response.status_code == 200
    get_element = ElementResponse(**get_response.json())
    
    # Compare relevant fields
    assert get_element.element_id == updated_element.element_id
    assert get_element.element_text == updated_element.element_text
    assert get_element.segment_id == updated_element.segment_id
    assert get_element.project_id == updated_element.project_id
    
    # Check that segment information is present in get_element
    assert get_element.segment is not None
    assert get_element.segment.segment_id == segment_id
    assert get_element.segment.segment_title == "Test Segment"

def test_update_segment(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    
    # Create a series
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    series_response = client.post("/series/", json=series_create.model_dump())
    assert series_response.status_code == 200
    series_id = series_response.json()["series_id"]
    
    # Create a segment
    segment_create = SegmentCreate(segment_title="Test Segment", series_id=series_id, project_id=project["project_id"])
    segment_response = client.post("/segments/", json=segment_create.model_dump())
    assert segment_response.status_code == 200
    segment_id = segment_response.json()["segment_id"]
    
    # Update the segment
    updated_title = "Updated Segment"
    segment_update = SegmentUpdate(segment_title=updated_title)
    update_response = client.put(f"/segments/{segment_id}", json=segment_update.model_dump())
    assert update_response.status_code == 200
    updated_segment = SegmentResponse(**update_response.json())
    
    # Check if the segment was updated correctly
    assert updated_segment.segment_id == segment_id
    assert updated_segment.segment_title == updated_title
    assert updated_segment.series_id == series_id
    assert updated_segment.project_id == project["project_id"]
    
    # Verify the update by getting the segment
    get_response = client.get(f"/segments/{segment_id}")
    assert get_response.status_code == 200
    get_segment = SegmentResponse(**get_response.json())
    
    # Compare relevant fields
    assert get_segment.segment_id == updated_segment.segment_id
    assert get_segment.segment_title == updated_segment.segment_title
    assert get_segment.series_id == updated_segment.series_id
    assert get_segment.project_id == updated_segment.project_id
    
    # Check that series information is present in get_segment
    assert get_segment.series is not None
    assert get_segment.series.series_id == series_id
    assert get_segment.series.series_title == "Test Series"

def test_create_batch_annotations(client: TestClient, create_project: Callable[..., Dict[str, Any]]) -> None:
    project = create_project()
    
    # Create a code type and codes
    code_type_create = CodeTypeCreate(type_name="Test Code Type", project_id=project["project_id"])
    code_type_response = client.post("/code_types/", json=code_type_create.model_dump())
    assert code_type_response.status_code == 200
    code_type_id = code_type_response.json()["type_id"]
    
    code_create_1 = CodeCreate(term="Code 1", description="Description 1", type_id=code_type_id, project_id=project["project_id"])
    code_create_2 = CodeCreate(term="Code 2", description="Description 2", type_id=code_type_id, project_id=project["project_id"])
    code_response_1 = client.post("/codes/", json=code_create_1.model_dump())
    code_response_2 = client.post("/codes/", json=code_create_2.model_dump())
    assert code_response_1.status_code == 200 and code_response_2.status_code == 200
    code_id_1 = code_response_1.json()["code_id"]
    code_id_2 = code_response_2.json()["code_id"]
    
    # Create a series, segment, and elements
    series_create = SeriesCreate(series_title="Test Series", project_id=project["project_id"])
    series_response = client.post("/series/", json=series_create.model_dump())
    assert series_response.status_code == 200
    series_id = series_response.json()["series_id"]
    
    segment_create = SegmentCreate(segment_title="Test Segment", series_id=series_id, project_id=project["project_id"])
    segment_response = client.post("/segments/", json=segment_create.model_dump())
    assert segment_response.status_code == 200
    segment_id = segment_response.json()["segment_id"]
    
    element_create_1 = ElementCreate(element_text="Element 1", segment_id=segment_id, project_id=project["project_id"])
    element_create_2 = ElementCreate(element_text="Element 2", segment_id=segment_id, project_id=project["project_id"])
    element_response_1 = client.post("/elements/", json=element_create_1.model_dump())
    element_response_2 = client.post("/elements/", json=element_create_2.model_dump())
    assert element_response_1.status_code == 200 and element_response_2.status_code == 200
    element_id_1 = element_response_1.json()["element_id"]
    element_id_2 = element_response_2.json()["element_id"]
    
    # Create batch annotations
    batch_annotation_create = BatchAnnotationCreate(
        element_ids=[element_id_1, element_id_2],
        code_ids=[code_id_1, code_id_2],
        project_id=project["project_id"]
    )
    response = client.post("/batch_annotations/", json=batch_annotation_create.model_dump())
    
    # Check the response
    assert response.status_code == 200
    created_annotations = response.json()
    assert len(created_annotations) == 4  # 2 elements * 2 codes = 4 annotations
    
    # Verify each created annotation
    for annotation in created_annotations:
        assert annotation["element_id"] in [element_id_1, element_id_2]
        assert annotation["code_id"] in [code_id_1, code_id_2]
        assert annotation["project_id"] == project["project_id"]
        assert "id" in annotation
        assert annotation["code"] is not None
        assert annotation["code"]["term"] in ["Code 1", "Code 2"]
