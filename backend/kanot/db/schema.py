from typing import Any

from sqlalchemy import (
    Column,
    Engine,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

# Define the base class for declarative models
Base = declarative_base()

# Define the CodeTypes class
class CodeType(Base): # type: ignore # type: ignore
    __tablename__ = 'code_types'
    type_id: Any = Column(Integer, primary_key=True, autoincrement=True)
    type_name: Any = Column(Text, unique=True, nullable=False)

# Define the Codes class
class Code(Base):
    __tablename__ = 'codes'
    code_id: Any = Column(Integer, primary_key=True, autoincrement=True)
    term: Any = Column(Text, unique=True, nullable=False)
    description: Any = Column(Text)
    type_id: Any = Column(Integer, ForeignKey('code_types.type_id'))
    reference: Any = Column(Text)
    coordinates: Any = Column(Text)
    code_type = relationship("CodeType")

    def __repr__(self):
        return f"Code(code_id={self.code_id}, term={self.term}, description={self.description}, type_id={self.type_id}, reference={self.reference}, coordinates={self.coordinates})"

# Define the Episodes class
class Episode(Base): # type: ignore
    __tablename__ = 'episodes'
    episode_id: Any = Column(String, primary_key=True)
    episode_title: Any = Column(Text, unique=True, nullable=False)

# Define the Transcripts class
class Transcript(Base): # type: ignore
    __tablename__ = 'transcripts'
    transcript_id: Any = Column(Integer, primary_key=True, autoincrement=True)
    transcript_text: Any = Column(Text)
    episode_id: Any = Column(String, ForeignKey('episodes.episode_id'))
    episode = relationship("Episode")

    def __repr__(self):
        return f"Transcript(transcript_id={self.transcript_id}, transcript_text={self.transcript_text}, episode_id={self.episode_id})"

# Define the Annotations class
class Annotation(Base): # type: ignore
    __tablename__ = 'annotations'
    annotation_id: Any = Column(Integer, primary_key=True, autoincrement=True)
    transcript_id: Any = Column(Integer, ForeignKey('transcripts.transcript_id'))
    code_id: Any = Column(Integer, ForeignKey('codes.code_id'))
    transcript = relationship("Transcript")
    code = relationship("Code")
    __table_args__ = (UniqueConstraint('transcript_id', 'code_id', name='_transcript_code_uc'),)

    def __repr__(self):
        return f"Annotation(annotation_id={self.annotation_id}, transcript_id={self.transcript_id}, code_id={self.code_id})"

# define the function to create the database
def create_database(engine: Engine):
    Base.metadata.create_all(engine)

# define the function to drop the database
def drop_database(engine: Engine):
    Base.metadata.drop_all(engine)