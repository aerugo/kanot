import warnings

import pytest
from sqlalchemy import create_engine
from sqlalchemy import exc as sa_exc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from kanot.db.schema import (
    Annotation,
    Code,
    CodeType,
    Episode,
    Transcript,
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

def test_create_episode(session: Session) -> None:
    episode = Episode(episode_id="EP001", episode_title="Test Episode")
    session.add(episode)
    session.commit()

    assert episode.episode_id == "EP001"
    assert episode.episode_title == "Test Episode"

def test_create_transcript(session: Session) -> None:
    episode = Episode(episode_id="EP001", episode_title="Test Episode")
    session.add(episode)
    session.commit()

    transcript = Transcript(transcript_text="Test Transcript", episode_id=episode.episode_id)
    session.add(transcript)
    session.commit()

    assert transcript.transcript_id is not None
    assert transcript.transcript_text == "Test Transcript"
    assert transcript.episode_id == episode.episode_id

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

    episode = Episode(episode_id="EP001", episode_title="Test Episode")
    session.add(episode)
    session.commit()

    transcript = Transcript(transcript_text="Test Transcript", episode_id=episode.episode_id)
    session.add(transcript)
    session.commit()

    annotation = Annotation(transcript_id=transcript.transcript_id, code_id=code.code_id)
    session.add(annotation)
    session.commit()

    assert annotation.annotation_id is not None
    assert annotation.transcript_id == transcript.transcript_id
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

    episode = Episode(episode_id="EP001", episode_title="Test Episode")
    session.add(episode)
    session.commit()

    transcript = Transcript(transcript_text="Test Transcript", episode_id=episode.episode_id)
    session.add(transcript)
    session.commit()

    annotation = Annotation(transcript_id=transcript.transcript_id, code_id=code.code_id)
    session.add(annotation)
    session.commit()

    # Test relationships
    assert code.code_type == code_type
    assert transcript.episode == episode
    assert annotation.transcript == transcript
    assert annotation.code == code

def test_unique_constraints(session: Session) -> None:
    # Test unique constraint on CodeType
    code_type1 = CodeType(type_name="Test Type")
    session.add(code_type1)
    session.commit()

    code_type2 = CodeType(type_name="Test Type")
    session.add(code_type2)
    with pytest.raises(Exception):  # SQLAlchemy will raise an exception for unique constraint violation
        session.commit()
    session.rollback()

    # Test unique constraint on Code
    code1 = Code(term="Test Code", type_id=code_type1.type_id)
    session.add(code1)
    session.commit()

    code2 = Code(term="Test Code", type_id=code_type1.type_id)
    session.add(code2)
    with pytest.raises(Exception):
        session.commit()
    session.rollback()

    # Test unique constraint on Episode
    episode1 = Episode(episode_id="EP001", episode_title="Test Episode")
    session.add(episode1)
    session.commit()

    episode2 = Episode(episode_id="EP001", episode_title="Another Test Episode")
    session.add(episode2)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=sa_exc.SAWarning)
        with pytest.raises(IntegrityError):
            session.commit()
    session.rollback()

    # Test unique constraint on Annotation
    transcript = Transcript(transcript_text="Test Transcript", episode_id=episode1.episode_id)
    session.add(transcript)
    session.commit()

    annotation1 = Annotation(transcript_id=transcript.transcript_id, code_id=code1.code_id)
    session.add(annotation1)
    session.commit()

    annotation2 = Annotation(transcript_id=transcript.transcript_id, code_id=code1.code_id)
    session.add(annotation2)
    with pytest.raises(Exception):
        session.commit()
    session.rollback()