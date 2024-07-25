import warnings

import pytest
from sqlalchemy import create_engine
from sqlalchemy import exc as sa_exc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db.schema import (
    Annotation,
    Code,
    CodeType,
    Element,
    Segment,
    create_database,
    drop_database,
)


@pytest.fixture(scope="function")
def engine():
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="function")
def session(engine):
    create_database(engine)
    session = Session(engine)
    yield session
    session.close()
    drop_database(engine)

def test_create_code_type(session: Session) -> None:
    code_type = CodeType(type_name="Test Type")
    session.add(code_type)
    session.commit()

    assert code_type.type_id is not None
    assert code_type.type_name == "Test Type"

def test_create_code(session: Session) -> None:
    code_type = CodeType(type_name="Test Type")
    session.add(code_type)
    session.commit()

    code = Code(
        term="Test Code",
        description="Test Description",
        type_id=code_type.type_id,
        reference="Test Reference",
        coordinates="Test Coordinates"
    )
    session.add(code)
    session.commit()

    assert code.code_id is not None
    assert code.term == "Test Code"
    assert code.description == "Test Description"
    assert code.type_id == code_type.type_id
    assert code.reference == "Test Reference"
    assert code.coordinates == "Test Coordinates"

def test_create_segment(session: Session) -> None:
    segment = Segment(segment_title="Test Segment")
    session.add(segment)
    session.commit()

    assert segment.segment_id == 1
    assert segment.segment_title == "Test Segment"

def test_create_element(session: Session) -> None:
    segment = Segment(segment_title="Test Segment")
    session.add(segment)
    session.commit()

    element = Element(element_text="Test Element", segment_id=segment.segment_id)
    session.add(element)
    session.commit()

    assert element.element_id is not None
    assert element.element_text == "Test Element"
    assert element.segment_id == segment.segment_id

def test_create_annotation(session: Session) -> None:
    code_type = CodeType(type_name="Test Type")
    session.add(code_type)
    session.commit()

    code = Code(
        term="Test Code",
        description="Test Description",
        type_id=code_type.type_id,
        reference="Test Reference",
        coordinates="Test Coordinates"
    )
    session.add(code)

    segment = Segment(segment_title="Test Segment")
    session.add(segment)
    session.commit()

    element = Element(element_text="Test Element", segment_id=segment.segment_id)
    session.add(element)
    session.commit()

    annotation = Annotation(element_id=element.element_id, code_id=code.code_id)
    session.add(annotation)
    session.commit()

    assert annotation.annotation_id is not None
    assert annotation.element_id == element.element_id
    assert annotation.code_id == code.code_id

def test_relationships(session: Session) -> None:
    code_type = CodeType(type_name="Test Type")
    session.add(code_type)
    session.commit()

    code = Code(
        term="Test Code",
        description="Test Description",
        type_id=code_type.type_id,
        reference="Test Reference",
        coordinates="Test Coordinates"
    )
    session.add(code)

    segment = Segment(segment_title="Test Segment")
    session.add(segment)
    session.commit()

    element = Element(element_text="Test Element", segment_id=segment.segment_id)
    session.add(element)
    session.commit()

    annotation = Annotation(element_id=element.element_id, code_id=code.code_id)
    session.add(annotation)
    session.commit()

    # Test relationships
    assert code.code_type == code_type
    assert element.segment == segment
    assert annotation.element == element
    assert annotation.code == code

def test_unique_constraints(session: Session) -> None:
    # Test unique constraint on CodeType
    code_type1 = CodeType(type_name="Test Type", project_id=1)
    session.add(code_type1)
    session.commit()

    code_type2 = CodeType(type_name="Test Type", project_id=1)
    session.add(code_type2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

    # Test unique constraint on Code
    code1 = Code(term="Test Code", type_id=code_type1.type_id, project_id=1)
    session.add(code1)
    session.commit()

    code2 = Code(term="Test Code", type_id=code_type1.type_id, project_id=1)
    session.add(code2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

    # Test unique constraint on Segment
    segment1 = Segment(segment_title="Test Segment", series_id=1, project_id=1)
    session.add(segment1)
    session.commit()

    segment2 = Segment(segment_title="Test Segment", series_id=1, project_id=1)
    session.add(segment2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

    # Test unique constraint on Annotation
    element = Element(element_text="Test Element", segment_id=segment1.segment_id, project_id=1)
    session.add(element)
    session.commit()

    annotation1 = Annotation(element_id=element.element_id, code_id=code1.code_id, project_id=1)
    session.add(annotation1)
    session.commit()

    annotation2 = Annotation(element_id=element.element_id, code_id=code1.code_id, project_id=1)
    session.add(annotation2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
