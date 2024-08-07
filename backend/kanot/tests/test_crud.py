import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from ..db.crud import DatabaseManager


@pytest.fixture
def db_engine() -> Engine:
    return create_engine('sqlite:///:memory:')

@pytest.fixture
def db_manager(db_engine: Engine) -> DatabaseManager:
    return DatabaseManager(db_engine)

# CodeType tests

def test_create_code_type(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    code_type = db_manager.read_code_type(1)
    assert code_type is not None
    assert code_type.type_name == "Test Type"

def test_read_code_type(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    code_type = db_manager.read_code_type(1)
    assert code_type is not None
    assert code_type.type_name == "Test Type"

def test_read_all_code_types(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type 1")
    db_manager.create_code_type("Test Type 2")
    code_types = db_manager.read_all_code_types()
    assert len(code_types) == 2
    assert code_types[0].type_name == "Test Type 1"
    assert code_types[1].type_name == "Test Type 2"

def test_update_code_type(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.update_code_type(1, "Updated Type")
    code_type = db_manager.read_code_type(1)
    assert code_type is not None
    assert code_type.type_name == "Updated Type"

def test_delete_code_type(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.delete_code_type(1)
    code_type = db_manager.read_code_type(1)
    assert code_type is None

# Code tests

def test_create_code(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    code = db_manager.read_code(1)
    assert code is not None
    assert code.term == "Test Code"

def test_read_code(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    code = db_manager.read_code(1)
    assert code is not None
    assert code.term == "Test Code"

def test_read_all_codes(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code 1", "Description 1", 1, "Reference 1", "Coordinates 1")
    db_manager.create_code("Test Code 2", "Description 2", 1, "Reference 2", "Coordinates 2")
    codes = db_manager.read_all_codes()
    assert len(codes) == 2
    assert codes[0].term == "Test Code 1"
    assert codes[1].term == "Test Code 2"

def test_update_code(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.update_code(1, term="Updated Code")
    code = db_manager.read_code(1)
    assert code is not None
    assert code.term == "Updated Code"

def test_delete_code(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.delete_code(1)
    code = db_manager.read_code(1)
    assert code is None

# Segment tests

def test_create_segment(db_manager: DatabaseManager) -> None:
    db_manager.create_segment("EP001", "Test Segment")
    segment = db_manager.read_segment("EP001")
    assert segment is not None
    assert segment.segment_title == "Test Segment"

def test_read_segment(db_manager: DatabaseManager) -> None:
    db_manager.create_segment("EP001", "Test Segment")
    segment = db_manager.read_segment("EP001")
    assert segment is not None
    assert segment.segment_title == "Test Segment"

def test_read_all_segments(db_manager: DatabaseManager) -> None:
    db_manager.create_segment("EP001", "Test Segment 1")
    db_manager.create_segment("EP002", "Test Segment 2")
    segments = db_manager.read_all_segments()
    assert len(segments) == 2
    assert segments[0].segment_title == "Test Segment 1"
    assert segments[1].segment_title == "Test Segment 2"

def test_update_segment(db_manager: DatabaseManager) -> None:
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.update_segment("EP001", "Updated Segment")
    segment = db_manager.read_segment("EP001")
    assert segment is not None
    assert segment.segment_title == "Updated Segment"

def test_delete_segment(db_manager: DatabaseManager) -> None:
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.delete_segment("EP001")
    segment = db_manager.read_segment("EP001")
    assert segment is None

# Element tests

def test_create_element(db_manager: DatabaseManager) -> None:
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.create_element("Test element", "EP001")
    element = db_manager.read_element(1)
    assert element is not None
    assert element.element_text == "Test element"

def test_read_element(db_manager: DatabaseManager) -> None:
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.create_element("Test element", "EP001")
    element = db_manager.read_element(1)
    assert element is not None
    assert element.element_text == "Test element"

def test_read_all_elements(db_manager: DatabaseManager) -> None:
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.create_element("Test element 1", "EP001")
    db_manager.create_element("Test element 2", "EP001")
    elements = db_manager.read_all_elements()
    assert len(elements) == 2
    assert elements[0].element_text == "Test element 1"
    assert elements[1].element_text == "Test element 2"

def test_update_element(db_manager: DatabaseManager) -> None:
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.create_element("Test element", "EP001")
    db_manager.update_element(1, element_text="Updated element")
    element = db_manager.read_element(1)
    assert element is not None
    assert element.element_text == "Updated element"

def test_delete_element(db_manager: DatabaseManager) -> None:
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.create_element("Test element", "EP001")
    db_manager.delete_element(1)
    element = db_manager.read_element(1)
    assert element is None

# Annotation tests

def test_create_annotation(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.create_element("Test element", "EP001")
    db_manager.create_annotation(1, 1)
    annotation = db_manager.read_annotation(1)
    assert annotation is not None
    assert annotation.element_id == 1
    assert annotation.code_id == 1

def test_read_annotation(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.create_element("Test element", "EP001")
    db_manager.create_annotation(1, 1)
    annotation = db_manager.read_annotation(1)
    assert annotation is not None
    assert annotation.element_id == 1
    assert annotation.code_id == 1

def test_read_all_annotations(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.create_code("Test Code 2", "Description 2", 1, "Reference 2", "Coordinates 2")
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.create_segment("EP002", "Test Segment 2")
    db_manager.create_element("Test element 1", "EP001")
    db_manager.create_element("Test element 2", "EP001")
    db_manager.create_element("Test element 3", "EP002")
    db_manager.create_annotation(1, 1)
    db_manager.create_annotation(1, 2)
    db_manager.create_annotation(2, 1)
    db_manager.create_annotation(2, 2)
    db_manager.create_annotation(3, 1)
    annotations = db_manager.read_all_annotations()
    assert len(annotations) == 5
    assert annotations[0].element_id == 1
    assert annotations[0].code_id == 1
    assert annotations[1].element_id == 1
    assert annotations[1].code_id == 2
    assert annotations[2].element_id == 2
    assert annotations[2].code_id == 1
    assert annotations[3].element_id == 2
    assert annotations[3].code_id == 2
    assert annotations[4].element_id == 3
    assert annotations[4].code_id == 1

def test_update_annotation(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.create_code("Test Code 2", "Description 2", 1, "Reference 2", "Coordinates 2")
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.create_element("Test element", "EP001")
    db_manager.create_annotation(1, 1)
    db_manager.update_annotation(1, code_id=2)
    annotation = db_manager.read_annotation(1)
    assert annotation is not None
    assert annotation.code_id == 2

def test_delete_annotation(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.create_element("Test element", "EP001")
    db_manager.create_annotation(1, 1)
    db_manager.delete_annotation(1)
    annotation = db_manager.read_annotation(1)
    assert annotation is None

# Merge codes test

def test_merge_codes(db_manager: DatabaseManager) -> None:
    # Create code types
    db_manager.create_code_type("Test Type")
    
    # Create two codes
    db_manager.create_code("Code A", "Description A", 1, "Reference A", "Coordinates A")
    db_manager.create_code("Code B", "Description B", 1, "Reference B", "Coordinates B")
    
    # Create an segment and two elements
    db_manager.create_segment("EP001", "Test Segment")
    db_manager.create_element("Test element 1", "EP001")
    db_manager.create_element("Test element 2", "EP001")
    
    # Create annotations for both codes
    db_manager.create_annotation(1, 1)  # Annotation for Code A, Element 1
    db_manager.create_annotation(2, 1)  # Annotation for Code A, Element 2
    db_manager.create_annotation(1, 2)  # Annotation for Code B, Element 1
    
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
    db_manager.create_code_type("Test Type")
    db_manager.create_code_type("Test Type")  # Should not raise an exception, but print a message
    
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")  # Should not raise an exception, but print a message

    db_manager.create_segment("EP001", "Test Segment")
    db_manager.create_segment("EP001", "Test Segment")  # Should not raise an exception, but print a message

    db_manager.create_element("Test element", "EP001")
    db_manager.create_element("Test element", "EP001")  # Should not raise an exception, but print a message

    db_manager.create_annotation(1, 1)
    db_manager.create_annotation(1, 1)  # Should not raise an exception, but print a message