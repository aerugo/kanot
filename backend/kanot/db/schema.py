from typing import List, Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class Project(Base):
    __tablename__ = 'projects'
    
    project_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_title: Mapped[str] = mapped_column(nullable=False)
    project_description: Mapped[Optional[str]] = mapped_column()

    code_types: Mapped[List["CodeType"]] = relationship(back_populates="project")
    codes: Mapped[List["Code"]] = relationship(back_populates="project")
    series: Mapped[List["Series"]] = relationship(back_populates="project")
    segments: Mapped[List["Segment"]] = relationship(back_populates="project")
    elements: Mapped[List["Element"]] = relationship(back_populates="project")
    annotations: Mapped[List["Annotation"]] = relationship(back_populates="project")

    def __repr__(self) -> str:
        return f"Project(project_id={self.project_id}, project_title={self.project_title}, project_description={self.project_description})"

class CodeType(Base):
    __tablename__ = 'code_types'
    
    type_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type_name: Mapped[str] = mapped_column(nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id'))

    project: Mapped["Project"] = relationship(back_populates="code_types")
    codes: Mapped[List["Code"]] = relationship(back_populates="code_type")
    
    __table_args__ = (UniqueConstraint('type_name', 'project_id', name='_type_name_project_uc'),)

    def __repr__(self) -> str:
        return f"CodeType(type_id={self.type_id}, type_name={self.type_name}, project_id={self.project_id})"

class Code(Base):
    __tablename__ = 'codes'
    
    code_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    term: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column()
    type_id: Mapped[int] = mapped_column(ForeignKey('code_types.type_id'))
    reference: Mapped[Optional[str]] = mapped_column()
    coordinates: Mapped[Optional[str]] = mapped_column()
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id'))

    code_type: Mapped["CodeType"] = relationship(back_populates="codes")
    project: Mapped["Project"] = relationship(back_populates="codes")

    __table_args__ = (UniqueConstraint('term', 'project_id', name='_term_project_uc'),)

    def __repr__(self) -> str:
        return f"Code(code_id={self.code_id}, term={self.term}, description={self.description}, type_id={self.type_id}, reference={self.reference}, coordinates={self.coordinates}, project_id={self.project_id})"

class Series(Base):
    __tablename__ = 'series'
    
    series_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    series_title: Mapped[str] = mapped_column(nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id'))

    project: Mapped["Project"] = relationship(back_populates="series")
    segments: Mapped[List["Segment"]] = relationship(back_populates="series")

class Segment(Base):
    __tablename__ = 'segments'
    
    segment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    segment_title: Mapped[str] = mapped_column(unique=True, nullable=False)
    series_id: Mapped[int] = mapped_column(ForeignKey('series.series_id'))
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id'))

    series: Mapped["Series"] = relationship(back_populates="segments")
    elements: Mapped[List["Element"]] = relationship(back_populates="segment")
    project: Mapped["Project"] = relationship(back_populates="segments")

class Element(Base):
    __tablename__ = 'elements'
    
    element_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    element_text: Mapped[str] = mapped_column(nullable=False, default="")
    segment_id: Mapped[int] = mapped_column(ForeignKey('segments.segment_id'))
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id'))

    segment: Mapped["Segment"] = relationship(back_populates="elements")
    annotations: Mapped[List["Annotation"]] = relationship(back_populates="element")
    project: Mapped["Project"] = relationship(back_populates="elements")

    def __repr__(self) -> str:
        return f"Element(element_id={self.element_id}, element_text={self.element_text}, segment_id={self.segment_id})"

class Annotation(Base):
    __tablename__ = 'annotations'
    
    annotation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    element_id: Mapped[int] = mapped_column(ForeignKey('elements.element_id'))
    code_id: Mapped[int] = mapped_column(ForeignKey('codes.code_id'))
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id'))

    element: Mapped["Element"] = relationship(back_populates="annotations")
    code: Mapped["Code"] = relationship()
    project: Mapped["Project"] = relationship(back_populates="annotations")

    __table_args__ = (UniqueConstraint('element_id', 'code_id', name='_element_code_uc'),)

    def __repr__(self) -> str:
        return f"Annotation(annotation_id={self.annotation_id}, element_id={self.element_id}, code_id={self.code_id})"

# The following functions remain unchanged
from sqlalchemy import Engine


def create_database(engine: Engine):
    Base.metadata.create_all(engine)

def drop_database(engine: Engine):
    Base.metadata.drop_all(engine)

# The SegmentCreate model remains unchanged as it's a Pydantic model, not an SQLAlchemy model
from pydantic import BaseModel


class SegmentCreate(BaseModel):
    segment_title: Optional[str]
    series_id: int
    project_id: int