import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db.schema import (
    Annotation,
    Code,
    CodeType,
    Element,
    Project,
    Segment,
    Series,
    create_database,
    drop_database,
)


@pytest.fixture(scope="function")
def engine():
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="function")
def session(engine: Engine):
    create_database(engine)
    session = Session(engine)
    yield session
    session.close()
    drop_database(engine)

def test_create_project(session: Session) -> None:
    project = Project(project_title="Test Project", project_description="Test Description")
    session.add(project)
    session.commit()

    assert project.project_id is not None
    assert project.project_title == "Test Project"
    assert project.project_description == "Test Description"

def test_create_code_type(session: Session) -> None:
    project = Project(project_title="Test Project")
    session.add(project)
    session.flush()

    code_type = CodeType(type_name="Test Type", project_id=project.project_id)
    session.add(code_type)
    session.commit()

    assert code_type.type_id is not None
    assert code_type.type_name == "Test Type"
    assert code_type.project_id == project.project_id

def test_create_code(session: Session) -> None:
    project = Project(project_title="Test Project")
    session.add(project)
    session.flush()

    code_type = CodeType(type_name="Test Type", project_id=project.project_id)
    session.add(code_type)
    session.flush()

    code = Code(
        term="Test Code",
        description="Test Description",
        type_id=code_type.type_id,
        reference="Test Reference",
        coordinates="Test Coordinates",
        project_id=project.project_id
    )
    session.add(code)
    session.commit()

    assert code.code_id is not None
    assert code.term == "Test Code"
    assert code.description == "Test Description"
    assert code.type_id == code_type.type_id
    assert code.reference == "Test Reference"
    assert code.coordinates == "Test Coordinates"
    assert code.project_id == project.project_id

def test_create_series(session: Session) -> None:
    project = Project(project_title="Test Project")
    session.add(project)
    session.flush()

    series = Series(series_title="Test Series", project_id=project.project_id)
    session.add(series)
    session.commit()

    assert series.series_id is not None
    assert series.series_title == "Test Series"
    assert series.project_id == project.project_id

def test_create_segment(session: Session) -> None:
    project = Project(project_title="Test Project")
    session.add(project)
    session.flush()

    series = Series(series_title="Test Series", project_id=project.project_id)
    session.add(series)
    session.flush()

    segment = Segment(segment_title="Test Segment", series_id=series.series_id, project_id=project.project_id)
    session.add(segment)
    session.commit()

    assert segment.segment_id is not None
    assert segment.segment_title == "Test Segment"
    assert segment.series_id == series.series_id
    assert segment.project_id == project.project_id

def test_create_element(session: Session) -> None:
    project = Project(project_title="Test Project")
    session.add(project)
    session.flush()

    series = Series(series_title="Test Series", project_id=project.project_id)
    session.add(series)
    session.flush()

    segment = Segment(segment_title="Test Segment", series_id=series.series_id, project_id=project.project_id)
    session.add(segment)
    session.flush()

    element = Element(element_text="Test Element", segment_id=segment.segment_id, project_id=project.project_id)
    session.add(element)
    session.commit()

    assert element.element_id is not None
    assert element.element_text == "Test Element"
    assert element.segment_id == segment.segment_id
    assert element.project_id == project.project_id

def test_create_annotation(session: Session) -> None:
    project = Project(project_title="Test Project")
    session.add(project)
    session.flush()

    code_type = CodeType(type_name="Test Type", project_id=project.project_id)
    session.add(code_type)
    session.flush()

    code = Code(
        term="Test Code",
        description="Test Description",
        type_id=code_type.type_id,
        reference="Test Reference",
        coordinates="Test Coordinates",
        project_id=project.project_id
    )
    session.add(code)
    session.flush()

    series = Series(series_title="Test Series", project_id=project.project_id)
    session.add(series)
    session.flush()

    segment = Segment(segment_title="Test Segment", series_id=series.series_id, project_id=project.project_id)
    session.add(segment)
    session.flush()

    element = Element(element_text="Test Element", segment_id=segment.segment_id, project_id=project.project_id)
    session.add(element)
    session.flush()

    annotation = Annotation(element_id=element.element_id, code_id=code.code_id, project_id=project.project_id)
    session.add(annotation)
    session.commit()

    assert annotation.annotation_id is not None
    assert annotation.element_id == element.element_id
    assert annotation.code_id == code.code_id
    assert annotation.project_id == project.project_id

def test_relationships(session: Session) -> None:
    project = Project(project_title="Test Project")
    session.add(project)
    session.flush()

    code_type = CodeType(type_name="Test Type", project_id=project.project_id)
    session.add(code_type)
    session.flush()

    code = Code(
        term="Test Code",
        description="Test Description",
        type_id=code_type.type_id,
        reference="Test Reference",
        coordinates="Test Coordinates",
        project_id=project.project_id
    )
    session.add(code)
    session.flush()

    series = Series(series_title="Test Series", project_id=project.project_id)
    session.add(series)
    session.flush()

    segment = Segment(segment_title="Test Segment", series_id=series.series_id, project_id=project.project_id)
    session.add(segment)
    session.flush()

    element = Element(element_text="Test Element", segment_id=segment.segment_id, project_id=project.project_id)
    session.add(element)
    session.flush()

    annotation = Annotation(element_id=element.element_id, code_id=code.code_id, project_id=project.project_id)
    session.add(annotation)
    session.commit()

    # Test relationships
    assert code.code_type == code_type
    assert element.segment == segment
    assert annotation.element == element
    assert annotation.code == code
    assert code_type.project == project
    assert code.project == project
    assert series.project == project
    assert segment.project == project
    assert element.project == project
    assert annotation.project == project

def test_unique_constraints(session: Session) -> None:
    project1 = Project(project_title="Test Project 1")
    project2 = Project(project_title="Test Project 2")
    session.add_all([project1, project2])
    session.flush()

    # Test unique constraint on CodeType
    code_type1 = CodeType(type_name="Test Type", project_id=project1.project_id)
    session.add(code_type1)
    session.commit()

    code_type2 = CodeType(type_name="Test Type", project_id=project1.project_id)
    session.add(code_type2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

    # Test unique constraint on Code
    code1 = Code(term="Test Code", type_id=code_type1.type_id, project_id=project1.project_id)
    session.add(code1)
    session.commit()

    code2 = Code(term="Test Code", type_id=code_type1.type_id, project_id=project1.project_id)
    session.add(code2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

    # Test unique constraint on Segment
    series1 = Series(series_title="Test Series", project_id=project1.project_id)
    session.add(series1)
    session.flush()

    segment1 = Segment(segment_title="Test Segment", series_id=series1.series_id, project_id=project1.project_id)
    session.add(segment1)
    session.commit()

    segment2 = Segment(segment_title="Test Segment", series_id=series1.series_id, project_id=project1.project_id)
    session.add(segment2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

    # Test unique constraint on Annotation
    element = Element(element_text="Test Element", segment_id=segment1.segment_id, project_id=project1.project_id)
    session.add(element)
    session.flush()

    annotation1 = Annotation(element_id=element.element_id, code_id=code1.code_id, project_id=project1.project_id)
    session.add(annotation1)
    session.commit()

    annotation2 = Annotation(element_id=element.element_id, code_id=code1.code_id, project_id=project1.project_id)
    session.add(annotation2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()