import logging
from logging.config import dictConfig
from typing import Any, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, sessionmaker

from .schema import (
    Annotation,
    Code,
    CodeType,
    Element,
    Project,
    Segment,
    Series,
    create_database,
)

# Define logging configuration
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - %(name)s - %(message)s",
            "use_colors": None,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "kanot": {"handlers": ["default"], "level": "INFO"}
    },
}

dictConfig(log_config)

# Initialize logger
logger = logging.getLogger("kanot")

class DatabaseManager:
    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.Session = sessionmaker(bind=engine)
        create_database(engine)

    def drop_database(self, engine: Any) -> None:
        drop_database(engine)

    # Project CRUD
    
    def create_project(self, project_title: str, project_description: Optional[str] = None) -> Project:
        session = self.Session()
        new_project = Project(project_title=project_title, project_description=project_description)
        try:
            session.add(new_project)
            session.commit()
            session.refresh(new_project)
            return new_project
        except IntegrityError:
            session.rollback()
            logger.error(f"Project with title={project_title} already exists.")
            return None
        finally:
            session.close()
    
    def read_project(self, project_id: int) -> Optional[Project]:
        session = self.Session()
        project = session.query(Project).filter_by(project_id=project_id).first()
        session.close()
        return project
    
    def read_all_projects(self) -> List[Project]:
        session = self.Session()
        projects = session.query(Project).all()
        session.close()
        return projects
    
    def update_project(self, project_id: int, project_title: Optional[str] = None, project_description: Optional[str] = None) -> None:
        session = self.Session()
        project = session.query(Project).filter_by(project_id=project_id).first()
        if project:
            if project_title:
                project.project_title = project_title
            if project_description is not None:
                project.project_description = project_description
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                logger.error(f"Failed to update Project with ID {project_id} due to a unique constraint violation.")
        session.close()
    
    def delete_project(self, project_id: int) -> None:
        session = self.Session()
        project = session.query(Project).filter_by(project_id=project_id).first()
        if project:
            session.delete(project)
            session.commit()
        session.close()

    # CodeType CRUD
    
    def create_code_type(self, type_name: str, project_id: int) -> CodeType | None:
        session = self.Session()
        new_code_type = CodeType(type_name=type_name, project_id=project_id)
        try:
            session.add(new_code_type)
            session.commit()
            session.refresh(new_code_type)
            return new_code_type
        except IntegrityError:
            session.rollback()
            logger.error(f"CodeType with type_name={type_name} already exists.")
            return None
        finally:
            session.close()
    
    def read_code_type(self, type_id: int) -> Optional[CodeType]:
        session = self.Session()
        code_type: Optional[CodeType] = session.query(CodeType).filter_by(type_id=type_id).first()
        session.close()
        return code_type
    
    def read_all_code_types(self) -> Optional[list[CodeType]]:
        session = self.Session()
        code_types = session.query(CodeType).all()
        session.close()
        return code_types
    
    def update_code_type(self, type_id: int, type_name: str) -> None:
        session = self.Session()
        code_type: Optional[CodeType] = session.query(CodeType).filter_by(type_id=type_id).first()
        if code_type:
            try:
                code_type.type_name = type_name
                session.commit()
            except IntegrityError:
                session.rollback()
                logger.error(f"Failed to update CodeType to type_name={type_name} due to a unique constraint violation.")
        session.close()
    
    def delete_code_type(self, type_id: int) -> None:
        session = self.Session()
        code_type: Optional[CodeType] = session.query(CodeType).filter_by(type_id=type_id).first()
        if code_type:
            session.delete(code_type)
            session.commit()
        session.close()

    # Code CRUD
    
    def create_code(self, term: str, description: str, type_id: int, reference: str, coordinates: str, project_id: int) -> Code | None:
        session = self.Session()
        try:
            new_code = Code(term=term, description=description, type_id=type_id, reference=reference, coordinates=coordinates, project_id=project_id)
            session.add(new_code)
            session.commit()
            session.refresh(new_code)
            return new_code
        except IntegrityError:
            session.rollback()
            logger.error(f"Code with term={term} already exists.")
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error in create_code: {str(e)}")
            raise
        finally:
            session.close()
    
    def read_code(self, code_id: int) -> Optional[Code]:
        session = self.Session()
        code: Optional[Code] = (
            session.query(Code)
            .options(joinedload(Code.code_type))
            .filter_by(code_id=code_id)
            .first()
        )
        session.close()
        return code

    def read_all_codes(self) -> Optional[list[Code]]:
        session = self.Session()
        codes = (
            session.query(Code)
            .options(joinedload(Code.code_type))
            .all()
        )
        session.close()
        return codes

    def update_code(self, code_id: int, term: Optional[str] = None, description: Optional[str] = None, type_id: Optional[int] = None, reference: Optional[str] = None, coordinates: Optional[str] = None) -> None:
        session = self.Session()
        code: Optional[Code] = session.query(Code).filter_by(code_id=code_id).first()
        if code:
            try:
                if term is not None:
                    code.term = term
                if description is not None:
                    code.description = description
                if type_id is not None:
                    code.type_id = type_id
                if reference is not None:
                    code.reference = reference
                if coordinates is not None:
                    code.coordinates = coordinates
                session.commit()
            except IntegrityError:
                session.rollback()
                logger.error("Failed to update Code due to a unique constraint violation.")
        session.close()
    
    def delete_code(self, code_id: int) -> None:
        session = self.Session()
        code: Optional[Code] = session.query(Code).filter_by(code_id=code_id).first()
        if code:
            session.delete(code)
            session.commit()
        session.close()

    # Series CRUD

    def create_series(self, series_title: str, project_id: int) -> Series | None:
        session = self.Session()
        new_series = Series(series_title=series_title, project_id=project_id)
        try:
            session.add(new_series)
            session.commit()
            session.refresh(new_series)
            return new_series
        except IntegrityError:
            session.rollback()
            logger.error(f"Series with series_title={series_title} already exists.")
            return None
        finally:
            session.close()

    def read_series(self, series_id: int) -> Optional[Series]:
        session = self.Session()
        series: Optional[Series] = session.query(Series).filter_by(series_id=series_id).first()
        session.close()
        return series
    
    def read_all_series(self) -> Optional[list[Series]]:
        session = self.Session()
        series = session.query(Series).all()
        session.close()
        return series
        
    def update_series(self, series_id: int, series_title: Optional[str]) -> None:
        session = self.Session()
        series: Optional[Series] = session.query(Series).filter_by(series_id=series_id).first()
        if series:
            try:
                if series_title is not None:
                    series.series_title = series_title
                session.commit()
            except IntegrityError:
                session.rollback()
                logger.error("Failed to update Series due to a unique constraint violation.")
        session.close()


    def delete_series(self, series_id: int) -> None:
        session = self.Session()
        series: Optional[Series] = session.query(Series).filter_by(series_id=series_id).first()
        if series:
            session.delete(series)
            session.commit()
        session.close()

    # Segment CRUD

    def create_segment(self, segment_title: Optional[str], series_id: int, project_id: int) -> Segment | None:
        session = self.Session()
        new_segment = Segment(segment_title=segment_title, series_id=series_id, project_id=project_id)
        try:
            session.add(new_segment)
            session.commit()
            session.refresh(new_segment)
            return new_segment
        except IntegrityError:
            session.rollback()
            logger.error(f"Segment with segment_title={segment_title} already exists.")
            return None
        finally:
            session.close()
    
    def read_segment(self, segment_id: int) -> Optional[Segment]:
        session = self.Session()
        segment: Optional[Segment] = session.query(Segment).filter_by(segment_id=segment_id).first()
        session.close()
        return segment
    
    def read_all_segments(self) -> Optional[list[Segment]]:
        session = self.Session()
        try:
            segments = (
                session.query(Segment)
                .options(joinedload(Segment.series))
                .all()
            )
            return segments
        finally:
            session.close()
    
    def update_segment(self, segment_id: int, segment_title: Optional[str] = None) -> None:
        session = self.Session()
        segment: Optional[Segment] = session.query(Segment).filter_by(segment_id=segment_id).first()
        if segment:
            try:
                if segment_title:
                    segment.segment_title = segment_title
                session.commit()
            except IntegrityError:
                session.rollback()
                logger.error("Failed to update Segment due to a unique constraint violation.")
        session.close()
    
    def delete_segment(self, segment_id: int) -> None:
        session = self.Session()
        segment: Optional[Segment] = session.query(Segment).filter_by(segment_id=segment_id).first()
        if segment:
            session.delete(segment)
            session.commit()
        session.close()

    # Element CRUD
    
    def create_element(self, element_text: str, segment_id: int, project_id: int) -> Element | None:
        session = self.Session()
        new_element = Element(element_text=element_text, segment_id=segment_id, project_id=project_id)
        try:
            session.add(new_element)
            session.commit()
            session.refresh(new_element)
            return new_element
        except IntegrityError:
            session.rollback()
            logger.error(f"Element for segment_id={segment_id} already exists.")
            return None
        finally:
            session.close()
    
    def read_element(self, element_id: int) -> Optional[Element]:
        session = self.Session()
        element: Optional[Element] = session.query(Element).filter_by(element_id=element_id).first()
        session.close()
        return element
    
    def read_all_elements(self) -> Optional[list[Element]]:
        session = self.Session()
        try:
            elements = (
                session.query(Element)
                .options(
                    joinedload(Element.segment).joinedload(Segment.series),
                    joinedload(Element.annotations).joinedload(Annotation.code).joinedload(Code.code_type)
                )
                .all()
            )
            return elements
        except Exception as e:
            logger.error(f"Error reading all elements: {str(e)}")
            return None
        finally:
            session.close()
    
    def read_elements_paginated(self, skip: int = 0, limit: int = 100) -> Optional[list[Element]]:
        session = self.Session()
        try:
            elements = (
                session.query(Element)
                .options(
                    joinedload(Element.segment).joinedload(Segment.series),
                    joinedload(Element.annotations).joinedload(Annotation.code).joinedload(Code.code_type)
                )
                .offset(skip)
                .limit(limit)
                .all()
            )
            return elements
        except Exception as e:
            logger.error(f"Error reading elements with pagination: {str(e)}")
            return None
        finally:
            session.close()

    def update_element(self, element_id: int, element_text: Optional[str] = None, segment_id: Optional[int] = None) -> None:
        session = self.Session()
        element: Optional[Element] = session.query(Element).filter_by(element_id=element_id).first()
        if element:
            try:
                if element_text:
                    element.element_text = element_text
                if segment_id:
                    element.segment_id = segment_id
                session.commit()
            except IntegrityError:
                session.rollback()
                logger.error("Failed to update Element due to a unique constraint violation.")
        session.close()
    
    def delete_element(self, element_id: int) -> None:
        session = self.Session()
        element: Optional[Element] = session.query(Element).filter_by(element_id=element_id).first()
        if element:
            session.delete(element)
            session.commit()
        session.close()

    # Annotation CRUD
        
    def create_annotation(self, element_id: int, code_id: int, project_id: int) -> Annotation | None:
        session = self.Session()
        try:
            new_annotation = Annotation(element_id=element_id, code_id=code_id, project_id=project_id)
            session.add(new_annotation)
            session.commit()
            
            # Fetch the annotation with its related code and code_type
            result = (
                session.query(Annotation)
                .options(joinedload(Annotation.code).joinedload(Code.code_type))
                .filter(Annotation.annotation_id == new_annotation.annotation_id)
                .first()
            )
            
            # Explicitly access the code and code_type to ensure they're loaded
            if result:
                _ = result.code
                if result.code:
                    _ = result.code.code_type
            
            session.refresh(result)
            return result
        except IntegrityError:
            session.rollback()
            logger.error(f"Annotation with element_id={element_id} and code_id={code_id} already exists.")
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating annotation: {str(e)}")
            return None
        finally:
            session.close()
        
    def read_annotation(self, annotation_id: int) -> Optional[Annotation]:
        session = self.Session()
        annotation: Optional[Annotation] = session.query(Annotation).filter_by(annotation_id=annotation_id).first()
        session.close()
        return annotation
    
    def read_all_annotations(self) -> Optional[list[Annotation]]:
        session = self.Session()
        annotations = session.query(Annotation).all()
        session.close()
        return annotations
    
    def update_annotation(self, annotation_id: int, element_id: Optional[int] = None, code_id: Optional[int] = None) -> None:
        session = self.Session()
        annotation: Optional[Annotation] = session.query(Annotation).filter_by(annotation_id=annotation_id).first()
        if annotation:
            try:
                if element_id:
                    annotation.element_id = element_id
                if code_id:
                    annotation.code_id = code_id
                session.commit()
            except IntegrityError:
                session.rollback()
                logger.error("Failed to update Annotation due to a unique constraint violation.")
        session.close()
    
    def delete_annotation(self, annotation_id: int) -> None:
        session = self.Session()
        annotation: Optional[Annotation] = session.query(Annotation).filter_by(annotation_id=annotation_id).first()
        if annotation:
            session.delete(annotation)
            session.commit()
        session.close()

# Merge codes

    def merge_codes(self, code_a_id: int, code_b_id: int) -> Code | None:
        session = self.Session()
        try:
            # Get both codes
            code_a = session.query(Code).filter_by(code_id=code_a_id).first()
            code_b = session.query(Code).filter_by(code_id=code_b_id).first()

            if not code_a or not code_b:
                logger.error(f"One or both codes (ID: {code_a_id}, {code_b_id}) do not exist.")
                return None

            # Get all annotations for code_a
            annotations_a = session.query(Annotation).filter_by(code_id=code_a_id).all()

            for annotation in annotations_a:
                # Check if there's already an annotation for this element with code_b
                existing_annotation = session.query(Annotation).filter(
                    and_(Annotation.element_id == annotation.element_id,
                         Annotation.code_id == code_b_id)
                ).first()

                if existing_annotation:
                    # If there's already an annotation, delete the one for code_a
                    session.delete(annotation)
                else:
                    # If there's no existing annotation, update this one to point to code_b
                    annotation.code_id = code_b_id

            # Delete code_a
            session.delete(code_a)

            session.commit()
            logger.info(f"Successfully merged Code {code_a_id} into Code {code_b_id}")

            return code_b
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to merge codes: {str(e)}")
            return None
        finally:
            session.close()

# Get annotations for code

    def get_annotations_for_code(self, code_id: int) -> list[Annotation]:
        session = self.Session()
        try:
            annotations = session.query(Annotation).filter_by(code_id=code_id).all()
            return annotations
        finally:
            session.close()

# Get codes for element

    def get_codes_for_element(self, element_id: int) -> list[Code]:
        session = self.Session()
        try:
            codes = (
                session.query(Code)
                .join(Annotation)
                .filter(Annotation.element_id == element_id)
                .all()
            )
            return codes
        finally:
            session.close()

    def get_annotations_for_element_and_code(self, element_id: int, code_id: int) -> list[Annotation]:
        session = self.Session()
        try:
            annotations = (
                session.query(Annotation)
                .options(joinedload(Annotation.code).joinedload(Code.code_type))
                .filter(Annotation.element_id == element_id, Annotation.code_id == code_id)
                .all()
            )
            return annotations
        finally:
            session.close()

# Search elements by string

    def search_elements(self, search_term: str, series_ids: list[int] = [], segment_ids: list[int] = [], code_ids: list[int] = [], skip: int = 0, limit: int = 100) -> Optional[list[Element]]:
        session = self.Session()
        try:
            query = (
                session.query(Element)
                .join(Element.segment)
                .join(Segment.series)
                .outerjoin(Element.annotations)
            )

            if search_term:
                query = query.filter(func.lower(Element.element_text).like(func.lower(f"%{search_term}%")))

            if series_ids:
                query = query.filter(Series.series_id.in_(series_ids))
            if segment_ids:
                query = query.filter(Segment.segment_id.in_(segment_ids))
            if code_ids:
                query = query.filter(Annotation.code_id.in_(code_ids))

            elements = (
                query.options(
                    joinedload(Element.segment).joinedload(Segment.series),
                    joinedload(Element.annotations).joinedload(Annotation.code).joinedload(Code.code_type)
                )
                .offset(skip)
                .limit(limit)
                .all()
            )
            return elements
        except Exception as e:
            logger.error(f"Error searching elements: {str(e)}")
            return None
        finally:
            session.close()

    def count_elements(self, search_term: str, series_ids: list[int] = [], segment_ids: list[int] = [], code_ids: list[int] = []) -> int:
        session = self.Session()
        try:
            query = session.query(func.count(Element.element_id)).join(Element.segment).join(Segment.series).outerjoin(Element.annotations)

            if search_term:
                query = query.filter(func.lower(Element.element_text).like(func.lower(f"%{search_term}%")))

            if series_ids:
                query = query.filter(Series.series_id.in_(series_ids))
            if segment_ids:
                query = query.filter(Segment.segment_id.in_(segment_ids))
            if code_ids:
                query = query.filter(Annotation.code_id.in_(code_ids))

            return query.scalar()
        finally:
            session.close()
