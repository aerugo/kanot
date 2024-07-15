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

# Episode tests

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

def test_read_all_episodes(db_manager: DatabaseManager) -> None:
    db_manager.create_episode("EP001", "Test Episode 1")
    db_manager.create_episode("EP002", "Test Episode 2")
    episodes = db_manager.read_all_episodes()
    assert len(episodes) == 2
    assert episodes[0].episode_title == "Test Episode 1"
    assert episodes[1].episode_title == "Test Episode 2"

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

# Transcript tests

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

def test_read_all_transcripts(db_manager: DatabaseManager) -> None:
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.create_transcript("Test transcript 1", "EP001")
    db_manager.create_transcript("Test transcript 2", "EP001")
    transcripts = db_manager.read_all_transcripts()
    assert len(transcripts) == 2
    assert transcripts[0].transcript_text == "Test transcript 1"
    assert transcripts[1].transcript_text == "Test transcript 2"

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

# Annotation tests

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

def test_read_all_annotations(db_manager: DatabaseManager) -> None:
    db_manager.create_code_type("Test Type")
    db_manager.create_code("Test Code", "Description", 1, "Reference", "Coordinates")
    db_manager.create_code("Test Code 2", "Description 2", 1, "Reference 2", "Coordinates 2")
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.create_episode("EP002", "Test Episode 2")
    db_manager.create_transcript("Test transcript 1", "EP001")
    db_manager.create_transcript("Test transcript 2", "EP001")
    db_manager.create_transcript("Test transcript 3", "EP002")
    db_manager.create_annotation(1, 1)
    db_manager.create_annotation(1, 2)
    db_manager.create_annotation(2, 1)
    db_manager.create_annotation(2, 2)
    db_manager.create_annotation(3, 1)
    annotations = db_manager.read_all_annotations()
    assert len(annotations) == 5
    assert annotations[0].transcript_id == 1
    assert annotations[0].code_id == 1
    assert annotations[1].transcript_id == 1
    assert annotations[1].code_id == 2
    assert annotations[2].transcript_id == 2
    assert annotations[2].code_id == 1
    assert annotations[3].transcript_id == 2
    assert annotations[3].code_id == 2
    assert annotations[4].transcript_id == 3
    assert annotations[4].code_id == 1

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

# Merge codes test

def test_merge_codes(db_manager: DatabaseManager) -> None:
    # Create code types
    db_manager.create_code_type("Test Type")
    
    # Create two codes
    db_manager.create_code("Code A", "Description A", 1, "Reference A", "Coordinates A")
    db_manager.create_code("Code B", "Description B", 1, "Reference B", "Coordinates B")
    
    # Create an episode and two transcripts
    db_manager.create_episode("EP001", "Test Episode")
    db_manager.create_transcript("Test transcript 1", "EP001")
    db_manager.create_transcript("Test transcript 2", "EP001")
    
    # Create annotations for both codes
    db_manager.create_annotation(1, 1)  # Annotation for Code A, Transcript 1
    db_manager.create_annotation(2, 1)  # Annotation for Code A, Transcript 2
    db_manager.create_annotation(1, 2)  # Annotation for Code B, Transcript 1
    
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
    
    # Check that we have annotations for both transcripts
    transcript_ids = set(annotation.transcript_id for annotation in annotations)
    assert transcript_ids == {1, 2}

# Integrity error handling test

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