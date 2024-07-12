import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from kanot.db.crud import DatabaseManager


@pytest.fixture
def db_engine() -> Engine:
    return create_engine('sqlite:///:memory:')

@pytest.fixture
def db_manager(db_engine: Engine) -> DatabaseManager:
    return DatabaseManager(db_engine)

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

def test_create_episode(db_manager: DatabaseManager) -> None:
    db_manager.create_episode("EP001", "Test Episode")
    episode = db_manager.read_episode("EP001")
    assert episode is not None
    assert episode.episode_title == "Test Episode"

def test_read_episode(db_manager: DatabaseManager) -> None:
    db_manager.create_episode("EP001", "Test Episode")
    episode = db_manager.read_episode("EP001")
    assert episode is not None
    assert episode.episode_title == "Test Episode"

def test_update_episode(db_manager: DatabaseManager) -> None:
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.update_episode("EP001", "Updated Episode")
    episode = db_manager.read_episode("EP001")
    assert episode is not None
    assert episode.episode_title == "Updated Episode"

def test_delete_episode(db_manager: DatabaseManager) -> None:
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.delete_episode("EP001")
    episode = db_manager.read_episode("EP001")
    assert episode is None

def test_create_transcript(db_manager: DatabaseManager) -> None:
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.create_transcript("Test transcript", "EP001")
    transcript = db_manager.read_transcript(1)
    assert transcript is not None
    assert transcript.transcript_text == "Test transcript"

def test_read_transcript(db_manager: DatabaseManager) -> None:
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.create_transcript("Test transcript", "EP001")
    transcript = db_manager.read_transcript(1)
    assert transcript is not None
    assert transcript.transcript_text == "Test transcript"

def test_update_transcript(db_manager: DatabaseManager) -> None:
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.create_transcript("Test transcript", "EP001")
    db_manager.update_transcript(1, transcript_text="Updated transcript")
    transcript = db_manager.read_transcript(1)
    assert transcript is not None
    assert transcript.transcript_text == "Updated transcript"

def test_delete_transcript(db_manager: DatabaseManager) -> None:
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.create_transcript("Test transcript", "EP001")
    db_manager.delete_transcript(1)
    transcript = db_manager.read_transcript(1)
    assert transcript is None

def test_create_annotation(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.create_transcript("Test transcript", "EP001")
    db_manager.create_annotation(1, 1)
    annotation = db_manager.read_annotation(1)
    assert annotation is not None
    assert annotation.transcript_id == 1
    assert annotation.code_id == 1

def test_read_annotation(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.create_transcript("Test transcript", "EP001")
    db_manager.create_annotation(1, 1)
    annotation = db_manager.read_annotation(1)
    assert annotation is not None
    assert annotation.transcript_id == 1
    assert annotation.code_id == 1

def test_update_annotation(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.create_code("Test Code 2", "Description 2", 1, "Reference 2", "Coordinates 2")
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.create_transcript("Test transcript", "EP001")
    db_manager.create_annotation(1, 1)
    db_manager.update_annotation(1, code_id=2)
    annotation = db_manager.read_annotation(1)
    assert annotation is not None
    assert annotation.code_id == 2

def test_delete_annotation(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.create_transcript("Test transcript", "EP001")
    db_manager.create_annotation(1, 1)
    db_manager.delete_annotation(1)
    annotation = db_manager.read_annotation(1)
    assert annotation is None

def test_integrity_error_handling(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code_type("Test Type")  # Should not raise an exception, but print a message
    
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")  # Should not raise an exception, but print a message

    db_manager.create_episode("EP001", "Test Episode")
    db_manager.create_episode("EP001", "Test Episode")  # Should not raise an exception, but print a message

    db_manager.create_transcript("Test transcript", "EP001")
    db_manager.create_transcript("Test transcript", "EP001")  # Should not raise an exception, but print a message

    db_manager.create_annotation(1, 1)
    db_manager.create_annotation(1, 1)  # Should not raise an exception, but print a message