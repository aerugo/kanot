from typing import Any

from sqlalchemy import Column, Engine, ForeignKey, Integer, Text, UniqueConstraint
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

class Series(Base):
    __tablename__ = 'series'
    series_id: Any = Column(Integer, primary_key=True, autoincrement=True)
    series_title: Any = Column(Text, nullable=False)

class Segment(Base):
    __tablename__ = 'segments'
    segment_id: Any = Column(Integer, primary_key=True)
    segment_title: Any = Column(Text, unique=True, nullable=False)
    series_id: Any = Column(Integer, ForeignKey('series.series_id'))
    series = relationship("Series")

class Element(Base):
    __tablename__ = 'elements'
    element_id: Any = Column(Integer, primary_key=True, autoincrement=True)
    element_text: Any = Column(Text, nullable=False, default="")
    segment_id: Any = Column(Integer, ForeignKey('segments.segment_id'))
    segment = relationship("Segment")
    annotations = relationship("Annotation", back_populates="element")

    def __repr__(self):
        return f"Element(element_id={self.element_id}, element_text={self.element_text}, segment_id={self.segment_id})"

class Annotation(Base): # type: ignore
    __tablename__ = 'annotations'
    annotation_id: Any = Column(Integer, primary_key=True, autoincrement=True)
    element_id: Any = Column(Integer, ForeignKey('elements.element_id'))
    code_id: Any = Column(Integer, ForeignKey('codes.code_id'))
    element = relationship("Element", back_populates="annotations")
    code = relationship("Code")
    __table_args__ = (UniqueConstraint('element_id', 'code_id', name='_element_code_uc'),)

    def __repr__(self):
        return f"Annotation(annotation_id={self.annotation_id}, element_id={self.element_id}, code_id={self.code_id})"

def create_database(engine: Engine):
    Base.metadata.create_all(engine)

def drop_database(engine: Engine):
    Base.metadata.drop_all(engine)