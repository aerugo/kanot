from typing import Any, Optional

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from ..db.crud import DatabaseManager
from ..db.schema import Project


@pytest.fixture
def db_engine() -> Engine:
    return create_engine('sqlite:///:memory:')

@pytest.fixture
def db_manager(db_engine: Engine) -> DatabaseManager:
    return DatabaseManager(db_engine)

@pytest.fixture
def project(db_manager: DatabaseManager) -> Optional[Project]:
    return db_manager.create_project("Test Project", "Test Description")

# Project tests

def test_create_project(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    assert project.project_title == "Test Project"
    assert project.project_description == "Test Description"

def test_read_project(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    read_project = db_manager.read_project(project.project_id)
    assert read_project is not None
    assert read_project.project_title == "Test Project"
    assert read_project.project_description == "Test Description"

def test_update_project(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.update_project(project.project_id, "Updated Project", "Updated Description")
    updated_project = db_manager.read_project(project.project_id)
    assert updated_project is not None
    assert updated_project.project_title == "Updated Project"
    assert updated_project.project_description == "Updated Description"

def test_delete_project(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.delete_project(project.project_id)
    deleted_project = db_manager.read_project(project.project_id)
    assert deleted_project is None

# CodeType tests

def test_create_code_type(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    new_code_type = db_manager.create_code_type("Test Type", project.project_id)
    assert new_code_type is not None
    assert new_code_type.type_name == "Test Type"
    assert new_code_type.project_id == project.project_id

    # Try to create the same code type again
    duplicate_code_type = db_manager.create_code_type("Test Type", project.project_id)
    assert duplicate_code_type is None

def test_read_all_code_types(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_code_type("Test Type 1", project.project_id)
    db_manager.create_code_type("Test Type 2", project.project_id)
    code_types = db_manager.read_all_code_types()
    assert code_types is not None
    assert len(code_types) == 2
    assert code_types[0].type_name == "Test Type 1"
    assert code_types[1].type_name == "Test Type 2"

def test_update_code_type(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_code_type("Test Type", project.project_id)
    db_manager.update_code_type(1, "Updated Type")
    code_type = db_manager.read_code_type(1)
    assert code_type is not None
    assert code_type.type_name == "Updated Type"

def test_delete_code_type(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_code_type("Test Type", project.project_id)
    db_manager.delete_code_type(1)
    code_type = db_manager.read_code_type(1)
    assert code_type is None

# Code tests

def test_create_code(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_code_type("Test Type", project.project_id)
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates", project.project_id)
    code = db_manager.read_code(1)
    assert code is not None
    assert code.term == "Test Code"
    assert code.project_id == project.project_id

def test_read_all_codes(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_code_type("Test Type", project.project_id)
    db_manager.create_code("Test Code 1", "Description 1", 1, "Reference 1", "Coordinates 1", project.project_id)
    db_manager.create_code("Test Code 2", "Description 2", 1, "Reference 2", "Coordinates 2", project.project_id)
    codes = db_manager.read_all_codes()
    assert codes is not None
    assert len(codes) == 2
    assert codes[0].term == "Test Code 1"
    assert codes[1].term == "Test Code 2"

def test_update_code(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_code_type("Test Type", project.project_id)
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates", project.project_id)
    db_manager.update_code(1, term="Updated Code")
    code = db_manager.read_code(1)
    assert code is not None
    assert code.term == "Updated Code"

def test_delete_code(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_code_type("Test Type", project.project_id)
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates", project.project_id)
    db_manager.delete_code(1)
    code = db_manager.read_code(1)
    assert code is None

# Series tests

def test_create_series(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_series("Test Series", project.project_id)
    series = db_manager.read_series(1)
    assert series is not None
    assert series.series_title == "Test Series"
    assert series.project_id == project.project_id

def test_read_all_series(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_series("Test Series 1", project.project_id)
    db_manager.create_series("Test Series 2", project.project_id)
    series = db_manager.read_all_series()
    assert series is not None
    assert len(series) == 2
    assert series[0].series_title == "Test Series 1"
    assert series[1].series_title == "Test Series 2"

def test_update_series(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_series("Test Series", project.project_id)
    db_manager.update_series(1, "Updated Series")
    series = db_manager.read_series(1)
    assert series is not None
    assert series.series_title == "Updated Series"

def test_delete_series(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_series("Test Series", project.project_id)
    db_manager.delete_series(1)
    series = db_manager.read_series(1)
    assert series is None

# Segment tests

def test_create_segment(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    segment = db_manager.read_segment(1)
    assert segment is not None
    assert segment.segment_title == "Test Segment"
    assert segment.project_id == project.project_id

def test_read_all_segments(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    db_manager.create_segment("Test Segment 1", series.series_id, project.project_id)
    db_manager.create_segment("Test Segment 2", series.series_id, project.project_id)
    segments = db_manager.read_all_segments()
    assert segments is not None
    assert len(segments) == 2
    assert segments[0].segment_title == "Test Segment 1"
    assert segments[1].segment_title == "Test Segment 2"

def test_update_segment(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    db_manager.update_segment(1, "Updated Segment")
    segment = db_manager.read_segment(1)
    assert segment is not None
    assert segment.segment_title == "Updated Segment"

def test_delete_segment(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    db_manager.delete_segment(1)
    segment = db_manager.read_segment(1)
    assert segment is None

# Element tests

def test_create_element(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    segment = db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    assert segment is not None
    db_manager.create_element("Test element", segment.segment_id, project.project_id)
    element = db_manager.read_element(1)
    assert element is not None
    assert element.element_text == "Test element"
    assert element.project_id == project.project_id

def test_read_all_elements(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    segment = db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    assert segment is not None
    db_manager.create_element("Test element 1", segment.segment_id, project.project_id)
    db_manager.create_element("Test element 2", segment.segment_id, project.project_id)
    elements = db_manager.read_all_elements()
    assert elements is not None
    assert len(elements) == 2
    assert elements[0].element_text == "Test element 1"
    assert elements[1].element_text == "Test element 2"

def test_update_element(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    segment = db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    assert segment is not None
    db_manager.create_element("Test element 1", segment.segment_id, project.project_id)
    db_manager.update_element(1, element_text="Updated element")
    element = db_manager.read_element(1)
    assert element is not None
    assert element.element_text == "Updated element"

def test_delete_element(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    segment = db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    assert segment is not None
    db_manager.create_element("Test element 1", segment.segment_id, project.project_id)
    db_manager.delete_element(1)
    element = db_manager.read_element(1)
    assert element is None

def test_update_element_text(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    segment = db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    assert segment is not None
    db_manager.create_element("Test element 1", segment.segment_id, project.project_id)
    
    # Update the element text
    db_manager.update_element(1, element_text="Updated element text")
    
    # Read the updated element
    updated_element = db_manager.read_element(1)
    assert updated_element is not None
    assert updated_element.element_text == "Updated element text"

def test_update_element_segment(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    segment1 = db_manager.create_segment("Test Segment 1", series.series_id, project.project_id)
    segment2 = db_manager.create_segment("Test Segment 2", series.series_id, project.project_id)
    assert segment1 is not None and segment2 is not None
    db_manager.create_element("Test element 1", segment1.segment_id, project.project_id)
    
    # Update the element's segment
    db_manager.update_element(1, segment_id=segment2.segment_id)
    
    # Read the updated element
    updated_element = db_manager.read_element(1)
    assert updated_element is not None
    assert updated_element.segment_id == segment2.segment_id

# Annotation tests

def test_create_annotation(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    segment = db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    assert segment is not None
    db_manager.create_element("Test element 1", segment.segment_id, project.project_id)
    db_manager.create_code_type("Test Type", project.project_id)
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates", project.project_id)
    db_manager.create_annotation(1, 1, project.project_id)
    annotation = db_manager.read_annotation(1)
    assert annotation is not None
    assert annotation.element_id == 1
    assert annotation.code_id == 1
    assert annotation.project_id == project.project_id

def test_read_annotation(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    segment = db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    assert segment is not None
    db_manager.create_element("Test element 1", segment.segment_id, project.project_id)
    db_manager.create_code_type("Test Type", project.project_id)
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates", project.project_id)
    db_manager.create_annotation(1, 1, project.project_id)
    annotation = db_manager.read_annotation(1)
    assert annotation is not None
    assert annotation.element_id == 1
    assert annotation.code_id == 1

def test_read_all_annotations(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_code_type("Test Type", project.project_id)
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates", project.project_id)
    db_manager.create_code("Test Code 2", "Description 2", 1, "Reference 2", "Coordinates 2", project.project_id)

    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None

    segment_1 = db_manager.create_segment("Test Segment 1", series.series_id, project.project_id)
    segment_2 = db_manager.create_segment("Test Segment 2", series.series_id, project.project_id)
    assert segment_1 is not None and segment_2 is not None

    db_manager.create_element("Test element 1", segment_1.segment_id, project.project_id)
    db_manager.create_element("Test element 2", segment_1.segment_id, project.project_id)
    db_manager.create_element("Test element 3", segment_2.segment_id, project.project_id)
    db_manager.create_annotation(1, 1, project.project_id)
    db_manager.create_annotation(1, 2, project.project_id)
    db_manager.create_annotation(2, 1, project.project_id)
    db_manager.create_annotation(2, 2, project.project_id)
    db_manager.create_annotation(3, 1, project.project_id)
    annotations: Optional[list[Any]] = db_manager.read_all_annotations()
    assert annotations is not None
    assert len(annotations) == 5
    assert annotations[0]['element_id'] == 1
    assert annotations[0]['code_id'] == 1
    assert annotations[1]['element_id'] == 1
    assert annotations[1]['code_id'] == 2
    assert annotations[2]['element_id'] == 2
    assert annotations[2]['code_id'] == 1
    assert annotations[3]['element_id'] == 2
    assert annotations[3]['code_id'] == 2
    assert annotations[4]['element_id'] == 3
    assert annotations[4]['code_id'] == 1

def test_update_annotation(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_code_type("Test Type", project.project_id)
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates", project.project_id)
    db_manager.create_code("Test Code 2", "Description 2", 1, "Reference 2", "Coordinates 2", project.project_id)
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    segment = db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    assert segment is not None
    db_manager.create_element("Test element", segment.segment_id, project.project_id)
    db_manager.create_annotation(1, 1, project.project_id)
    db_manager.update_annotation(1, code_id=2)
    annotation = db_manager.read_annotation(1)
    assert annotation is not None
    assert annotation.code_id == 2

def test_delete_annotation(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_code_type("Test Type", project.project_id)
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates", project.project_id)
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    segment = db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    assert segment is not None
    db_manager.create_element("Test element", segment.segment_id, project.project_id)
    db_manager.create_annotation(1, 1, project.project_id)
    db_manager.delete_annotation(1)
    annotation = db_manager.read_annotation(1)
    assert annotation is None

# Merge codes test

def test_merge_codes(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    # Create code types
    db_manager.create_code_type("Test Type", project.project_id)
    
    # Create two codes
    db_manager.create_code("Code A", "Description A", 1, "Reference A", "Coordinates A", project.project_id)
    db_manager.create_code("Code B", "Description B", 1, "Reference B", "Coordinates B", project.project_id)
    
    # Create a series and a segment
    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None
    segment = db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    assert segment is not None

    # Create an segment and two elements
    db_manager.create_element("Test element 1", segment.segment_id, project.project_id)
    db_manager.create_element("Test element 2", segment.segment_id, project.project_id)
    
    # Create annotations for both codes
    db_manager.create_annotation(1, 1, project.project_id)  # Annotation for Code A, Element 1
    db_manager.create_annotation(2, 1, project.project_id)  # Annotation for Code A, Element 2
    db_manager.create_annotation(1, 2, project.project_id)  # Annotation for Code B, Element 1
    
    # Merge Code A (id=1) into Code B (id=2)
    db_manager.merge_codes(1, 2)
    
    # Check if Code A has been deleted
    assert db_manager.read_code(1) is None
    
    # Check if annotations now point to Code B
    annotations = db_manager.get_annotations_for_code(2)
    assert len(annotations) == 2  # We expect 2 annotations now
    
    # Check if Code B still exists
    code_b = db_manager.read_code(2)
    assert code_b is not None
    assert code_b.term == "Code B"
    
    # Check that we have annotations for both elements
    element_ids = set(annotation.element_id for annotation in annotations)
    assert element_ids == {1, 2}

# Integrity error handling test

def test_integrity_error_handling(db_manager: DatabaseManager) -> None:
    project = db_manager.create_project("Test Project", "Test Description")
    assert project is not None
    db_manager.create_code_type("Test Type", project.project_id)
    db_manager.create_code_type("Test Type", project.project_id)  # Should not raise an exception, but print a message
    
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates", project.project_id)
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates", project.project_id)  # Should not raise an exception, but print a message

    series = db_manager.create_series("Test Series", project.project_id)
    assert series is not None

    db_manager.create_segment("Test Segment", series.series_id, project.project_id)
    db_manager.create_segment("Test Segment", series.series_id, project.project_id)  # Should not raise an exception, but print a message

    db_manager.create_element("Test element", series.series_id, project.project_id)
    db_manager.create_element("Test element", series.series_id, project.project_id)  # Should not raise an exception, but print a message

    db_manager.create_annotation(1, 1, project.project_id)
    db_manager.create_annotation(1, 1, project.project_id)  # Should not raise an exception, but print a message
