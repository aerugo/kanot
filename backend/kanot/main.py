from __future__ import annotations

import logging
import os
from logging.config import dictConfig
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from .db.crud import DatabaseManager
from .models import (
    AnnotationCreate,
    AnnotationResponse,
    AnnotationUpdate,
    BatchAnnotationCreate,
    BatchAnnotationRemove,
    CodeCreate,
    CodeResponse,
    CodeTypeCreate,
    CodeTypeResponse,
    CodeTypeUpdate,
    CodeUpdate,
    ElementCreate,
    ElementResponse,
    ElementUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    SegmentCreate,
    SegmentResponse,
    SegmentUpdate,
    SeriesCreate,
    SeriesResponse,
    SeriesUpdate,
)

# LOGGING

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

# DATABASE

def configure_database(database_url: str | None = None):
    if database_url is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///local_database.db")
    
    logger.info(f"Using database URL: {database_url}")
    engine = create_engine(database_url)
    logger.info(f"Local sqlite database on : {Path(database_url).resolve()}")
    return DatabaseManager(engine)

def get_db(database_url: str | None = None):
    db_manager = configure_database(database_url)
    return db_manager

def get_db_session():
    db_manager = get_db()
    with db_manager.get_session() as session:
        yield session

# ROUTER

router = APIRouter()

# PROJECTS

@router.post("/projects/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db_manager: DatabaseManager = Depends(get_db)
) -> ProjectResponse:
    if not project.project_title:
        raise HTTPException(status_code=422, detail="Project title cannot be empty")
    new_project = db_manager.create_project(project.project_title, project.project_description)
    if new_project is None:
        raise HTTPException(status_code=400, detail="Failed to create project")
    return ProjectResponse(
        id=new_project.project_id,
        project_id=new_project.project_id,
        project_title=new_project.project_title,
        project_description=new_project.project_description
    )

@router.get("/projects/", response_model=List[ProjectResponse])
def read_projects(
    db_manager: DatabaseManager = Depends(get_db)
) -> List[ProjectResponse]:
    projects = db_manager.read_all_projects()
    return [ProjectResponse.model_validate(project) for project in projects]

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def read_project(
    project_id: int,
    db_manager: DatabaseManager = Depends(get_db)
) -> ProjectResponse:
    project = db_manager.read_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(
        id=project.project_id,
        project_id=project.project_id,
        project_title=project.project_title,
        project_description=project.project_description
    )

@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project: ProjectUpdate,
    db_manager: DatabaseManager = Depends(get_db)
) -> ProjectResponse:
    updated_project = db_manager.update_project(project_id, project.project_title, project.project_description)
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(
        id=updated_project.project_id,
        project_id=updated_project.project_id,
        project_title=updated_project.project_title,
        project_description=updated_project.project_description
    )

@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db_manager: DatabaseManager = Depends(get_db)
):
    project = db_manager.read_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db_manager.delete_project(project_id)
    return {"message": "Project deleted successfully"}

# CodeType endpoints
@router.post("/code_types/", response_model=CodeTypeResponse)
def create_code_type(
    code_type: CodeTypeCreate,
    db_manager: DatabaseManager = Depends(get_db)
) -> CodeTypeResponse:
    new_code_type = db_manager.create_code_type(code_type.type_name, code_type.project_id)
    if new_code_type is None:
        raise HTTPException(status_code=400, detail=f"Code type '{code_type.type_name}' already exists in this project")
    return CodeTypeResponse(
        id=new_code_type.type_id,
        project_id=new_code_type.project_id,
        type_name=new_code_type.type_name,
        type_id=new_code_type.type_id
    )

@router.get("/code_types/", response_model=List[CodeTypeResponse])
def read_code_types(
    db_manager: DatabaseManager = Depends(get_db)
) -> List[CodeTypeResponse]:
    code_types = db_manager.read_all_code_types()
    assert code_types is not None
    return [CodeTypeResponse(
        id=code_type.type_id,
        project_id=code_type.project_id,
        type_id=code_type.type_id,
        type_name=code_type.type_name
    ) for code_type in code_types]

@router.get("/code_types/{type_id}", response_model=CodeTypeResponse)
def read_code_type(
    type_id: int,
    db_manager: DatabaseManager = Depends(get_db)
) -> CodeTypeResponse:
    code_type = db_manager.read_code_type(type_id)
    if code_type is None:
        raise HTTPException(status_code=404, detail="Code type not found")
    return CodeTypeResponse.model_validate(code_type)

@router.put("/code_types/{type_id}", response_model=CodeTypeResponse)
def update_code_type(
    type_id: int,
    code_type: CodeTypeUpdate,
    db_manager: DatabaseManager = Depends(get_db)
) -> CodeTypeResponse:
    if not code_type.type_name:
        raise HTTPException(status_code=422, detail="Code type name cannot be empty")
    db_manager.update_code_type(type_id, code_type.type_name)
    updated_code_type = db_manager.read_code_type(type_id)
    if updated_code_type is None:
        raise HTTPException(status_code=404, detail="Code type not found")
    return CodeTypeResponse.model_validate(updated_code_type)

@router.delete("/code_types/{type_id}")
def delete_code_type(
    type_id: int,
    db_manager: DatabaseManager = Depends(get_db)
):
    db_manager.delete_code_type(type_id)
    return {"message": "Code type deleted successfully"}

# Code endpoints
@router.post("/codes/", response_model=CodeResponse)
def create_code(
    code: CodeCreate,
    db_manager: DatabaseManager = Depends(get_db)
) -> CodeResponse:
    if not code.term:
        raise HTTPException(status_code=422, detail="Code term cannot be empty")
    if not code.type_id:
        raise HTTPException(status_code=422, detail="Code type ID cannot be empty")
    if not code.project_id:
        raise HTTPException(status_code=422, detail="Project ID cannot be empty")
    new_code = db_manager.create_code(
        code.term, code.description, code.type_id,
        code.reference, code.coordinates, code.project_id
    )
    if new_code is None:
        raise HTTPException(status_code=400, detail="Failed to create code")
    return CodeResponse(
        id=new_code.code_id,
        code_id=new_code.code_id,
        term=new_code.term,
        description=new_code.description,
        type_id=new_code.type_id,
        reference=new_code.reference,
        coordinates=new_code.coordinates,
        project_id=new_code.project_id,
        code_type=CodeTypeResponse(
            id=new_code.code_type.type_id,
            type_id=new_code.code_type.type_id,
            type_name=new_code.code_type.type_name,
            project_id=new_code.code_type.project_id
        ) if new_code.code_type else None
    )

@router.get("/codes/", response_model=List[CodeResponse])
def read_codes(
    db_manager: DatabaseManager = Depends(get_db)
) -> List[CodeResponse]:
    codes = db_manager.read_all_codes()
    assert codes is not None
    return [CodeResponse.model_validate({
        "id": code.code_id,
        "code_id": code.code_id,
        "term": code.term,
        "description": code.description,
        "type_id": code.type_id,
        "reference": code.reference,
        "coordinates": code.coordinates,
        "project_id": code.project_id,
        "code_type": CodeTypeResponse.model_validate({
            "id": code.code_type.type_id,
            "type_id": code.code_type.type_id,
            "type_name": code.code_type.type_name,
            "project_id": code.code_type.project_id
        }) if code.code_type else None
    }) for code in codes]

@router.get("/codes/{code_id}", response_model=CodeResponse)
def read_code(
    code_id: int,
    db_manager: DatabaseManager = Depends(get_db)
) -> CodeResponse:
    code = db_manager.read_code(code_id)
    if code is None:
        raise HTTPException(status_code=404, detail="Code not found")
    return CodeResponse.model_validate({
        "id": code.code_id,
        "code_id": code.code_id,
        "term": code.term,
        "description": code.description,
        "type_id": code.type_id,
        "reference": code.reference,
        "coordinates": code.coordinates,
        "project_id": code.project_id,
        "code_type": CodeTypeResponse.model_validate({
            "id": code.code_type.type_id,
            "type_id": code.code_type.type_id,
            "type_name": code.code_type.type_name,
            "project_id": code.code_type.project_id
        }) if code.code_type else None
    })

@router.put("/codes/{code_id}", response_model=CodeResponse)
def update_code(
    code_id: int,
    code: CodeUpdate,
    db_manager: DatabaseManager = Depends(get_db)
) -> CodeResponse:
    db_manager.update_code(
        code_id, code.term, code.description, 
        code.type_id, code.reference, code.coordinates
    )
    updated_code = db_manager.read_code(code_id)
    if updated_code is None:
        raise HTTPException(status_code=404, detail="Code not found")
    return CodeResponse.model_validate(updated_code)

@router.delete("/codes/{code_id}")
def delete_code(
    code_id: int,
    db_manager: DatabaseManager = Depends(get_db)
):
    db_manager.delete_code(code_id)
    return {"message": "Code deleted successfully"}

# Series endpoints
@router.post("/series/", response_model=SeriesResponse)
def create_series(
    series: SeriesCreate,
    db_manager: DatabaseManager = Depends(get_db)
) -> SeriesResponse:
    new_series = db_manager.create_series(series.series_title, series.project_id)
    if new_series is None:
        raise HTTPException(status_code=400, detail="Failed to create series")
    return SeriesResponse(
        id=new_series.series_id,
        project_id=new_series.project_id,
        series_id=new_series.series_id,
        series_title=new_series.series_title
    )

@router.get("/series/", response_model=List[SeriesResponse])
def read_all_series(
    db_manager: DatabaseManager = Depends(get_db)
) -> List[SeriesResponse]:
    series_list = db_manager.read_all_series()
    assert series_list is not None
    return [SeriesResponse(
        id=series.series_id,
        project_id=series.project_id,
        series_id=series.series_id,
        series_title=series.series_title
    ) for series in series_list]

@router.get("/series/{series_id}", response_model=SeriesResponse)
def read_series(
    series_id: int,
    db_manager: DatabaseManager = Depends(get_db)
) -> SeriesResponse:
    series = db_manager.read_series(series_id)
    if series is None:
        raise HTTPException(status_code=404, detail="Series not found")
    return SeriesResponse.model_validate(series)

@router.put("/series/{series_id}", response_model=SeriesResponse)
def update_series(
    series_id: int,
    series: SeriesUpdate,
    db_manager: DatabaseManager = Depends(get_db)
) -> SeriesResponse:
    db_manager.update_series(series_id, series.series_title)
    updated_series = db_manager.read_series(series_id)
    if updated_series is None:
        raise HTTPException(status_code=404, detail="Series not found")
    return SeriesResponse.model_validate(updated_series)

@router.delete("/series/{series_id}")
def delete_series(
    series_id: int,
    db_manager: DatabaseManager = Depends(get_db)
):
    db_manager.delete_series(series_id)
    return {"message": "Series deleted successfully"}

# Segment endpoints
@router.post("/segments/", response_model=SegmentResponse)
def create_segment(
    segment: SegmentCreate,
    db_manager: DatabaseManager = Depends(get_db)
) -> SegmentResponse:
    new_segment = db_manager.create_segment(segment.segment_title, segment.series_id, segment.project_id)
    if new_segment is None:
        existing_segment = db_manager.read_segment_by_title(segment.segment_title, segment.series_id)
        if existing_segment:
            return SegmentResponse.model_validate(existing_segment)
        raise HTTPException(status_code=400, detail="Failed to create segment")
    return SegmentResponse(
        id=new_segment.segment_id,
        segment_id=new_segment.segment_id,
        segment_title=new_segment.segment_title,
        series_id=new_segment.series_id,
        project_id=new_segment.project_id,
        series=None  # We're not loading the series here to avoid the DetachedInstanceError
    )

@router.get("/segments/", response_model=List[SegmentResponse])
def read_segments(
    db_manager: DatabaseManager = Depends(get_db)
) -> List[SegmentResponse]:
    segments = db_manager.read_all_segments()
    assert segments is not None
    return [SegmentResponse.model_validate({
        "id": segment.segment_id,
        "segment_id": segment.segment_id,
        "segment_title": segment.segment_title,
        "series_id": segment.series_id,
        "project_id": segment.project_id,
        "series": SeriesResponse.model_validate({
            "id": segment.series.series_id,
            "series_id": segment.series.series_id,
            "series_title": segment.series.series_title,
            "project_id": segment.series.project_id
        }) if segment.series else None
    }) for segment in segments]

@router.get("/segments/{segment_id}", response_model=SegmentResponse)
def read_segment(
    segment_id: int,
    db_manager: DatabaseManager = Depends(get_db)
) -> SegmentResponse:
    segment = db_manager.read_segment(segment_id)
    if segment is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    return SegmentResponse.model_validate(segment)

@router.put("/segments/{segment_id}", response_model=SegmentResponse)
def update_segment(
    segment_id: int,
    segment: SegmentUpdate,
    db_manager: DatabaseManager = Depends(get_db)
) -> SegmentResponse:
    updated_segment = db_manager.update_segment(segment_id, segment.segment_title)
    if updated_segment is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    return SegmentResponse.model_validate(updated_segment)

@router.delete("/segments/{segment_id}")
def delete_segment(
    segment_id: int,
    db_manager: DatabaseManager = Depends(get_db)
):
    db_manager.delete_segment(segment_id)
    return {"message": "Segment deleted successfully"}

# Element endpoints
@router.post("/elements/", response_model=ElementResponse)
def create_element(
    element: ElementCreate,
    db_manager: DatabaseManager = Depends(get_db)
) -> ElementResponse:
    # Check if the segment exists
    segment = db_manager.read_segment(element.segment_id)
    if segment is None:
        raise HTTPException(status_code=404, detail="Segment not found")
        
    # Check if the project exists
    project = db_manager.read_project(element.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
        
    new_element = db_manager.create_element(element.element_text, element.segment_id, element.project_id)
    if new_element is None:
        raise HTTPException(status_code=400, detail="Failed to create element")
    response = ElementResponse(
        id=new_element.element_id,
        element_text=new_element.element_text,
        segment_id=new_element.segment_id,
        project_id=new_element.project_id,
        segment=SegmentResponse(
            id=new_element.segment.segment_id,
            segment_id=new_element.segment.segment_id,
            segment_title=new_element.segment.segment_title,
            series_id=new_element.segment.series_id,
            project_id=new_element.segment.project_id,
            series=None
        ) if new_element.segment else None,
        annotations=[]
    )
    return response

@router.get("/elements/", response_model=List[ElementResponse])
def read_elements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db_manager: DatabaseManager = Depends(get_db)
) -> List[ElementResponse]:
    elements = db_manager.read_elements_paginated(skip=skip, limit=limit)
    if elements is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve elements")
    return [ElementResponse.model_validate({
        "id": element.element_id,
        "element_id": element.element_id,
        "element_text": element.element_text,
        "segment_id": element.segment_id,
        "project_id": element.project_id,
        "segment": SegmentResponse.model_validate({
            "id": element.segment.segment_id,
            "segment_id": element.segment.segment_id,
            "segment_title": element.segment.segment_title,
            "series_id": element.segment.series_id,
            "project_id": element.segment.project_id,
            "series": None
        }) if element.segment else None,
        "annotations": []
    }) for element in elements]

@router.get("/elements/{element_id}", response_model=ElementResponse)
def read_element(
    element_id: int,
    db_manager: DatabaseManager = Depends(get_db)
) -> ElementResponse:
    element = db_manager.read_element(element_id)
    if element is None:
        raise HTTPException(status_code=404, detail="Element not found")
    return ElementResponse.model_validate(element)

@router.put("/elements/{element_id}", response_model=ElementResponse)
def update_element(
    element_id: int,
    element: ElementUpdate,
    db_manager: DatabaseManager = Depends(get_db)
) -> ElementResponse:
    updated_element = db_manager.update_element(element_id, element.element_text, element.segment_id)
    if updated_element is None:
        raise HTTPException(status_code=404, detail="Element not found")
    return ElementResponse.model_validate(updated_element)

@router.delete("/elements/{element_id}")
def delete_element(
    element_id: int,
    db_manager: DatabaseManager = Depends(get_db)
):
    db_manager.delete_element(element_id)
    return {"message": "Element deleted successfully"}

# Annotation endpoints
@router.post("/annotations/", response_model=AnnotationResponse)
def create_annotation(
    annotation: AnnotationCreate,
    db_manager: DatabaseManager = Depends(get_db)
) -> AnnotationResponse:
    try:
        new_annotation = db_manager.create_annotation(annotation.element_id, annotation.code_id, annotation.project_id)
        if new_annotation is None:
            raise HTTPException(status_code=400, detail="Failed to create annotation")
        return AnnotationResponse(
            id=new_annotation.annotation_id,
            element_id=new_annotation.element_id,
            code_id=new_annotation.code_id,
            project_id=new_annotation.project_id,
            code=CodeResponse(
                id=new_annotation.code.code_id,
                code_id=new_annotation.code.code_id,
                term=new_annotation.code.term,
                description=new_annotation.code.description,
                type_id=new_annotation.code.type_id,
                reference=new_annotation.code.reference,
                coordinates=new_annotation.code.coordinates,
                project_id=new_annotation.code.project_id,
                code_type=None
            ) if new_annotation.code else None
        )
    except Exception as e:
        logger.error(f"Error creating annotation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating annotation: {str(e)}")

@router.post("/batch_annotations/", response_model=List[AnnotationResponse])
def create_batch_annotations(
    batch_data: BatchAnnotationCreate,
    db_manager: DatabaseManager = Depends(get_db)
) -> List[AnnotationResponse]:
    new_annotations: List[AnnotationResponse] = []
    for element_id in batch_data.element_ids:
        for code_id in batch_data.code_ids:
            annotation = db_manager.create_annotation(element_id, code_id, project_id=batch_data.project_id)
            if annotation:
                new_annotations.append(AnnotationResponse.model_validate(annotation))
    return new_annotations

@router.delete("/batch_annotations/", response_model=List[AnnotationResponse])
def remove_batch_annotations(
    batch_data: BatchAnnotationRemove,
    db_manager: DatabaseManager = Depends(get_db)
) -> List[AnnotationResponse]:
    try:
        removed_annotations: List[AnnotationResponse] = []
        for element_id in batch_data.element_ids:
            for code_id in batch_data.code_ids:
                annotations = db_manager.get_annotations_for_element_and_code(element_id, code_id)
                for annotation in annotations:
                    db_manager.delete_annotation(annotation.annotation_id)
                    removed_annotations.append(AnnotationResponse.model_validate(annotation))
        return removed_annotations
    except Exception as e:
        logger.error(f"Error in batch annotation removal: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during batch annotation removal")

@router.get("/annotations/", response_model=List[AnnotationResponse])
def read_annotations(
    db_manager: DatabaseManager = Depends(get_db)
) -> List[AnnotationResponse]:
    annotations = db_manager.read_all_annotations()
    assert annotations is not None
    return [AnnotationResponse(
        id=annotation['annotation_id'],
        element_id=annotation['element_id'],
        code_id=annotation['code_id'],
        project_id=annotation['project_id'],
        code=CodeResponse(
            id=annotation['code']['code_id'],
            code_id=annotation['code']['code_id'],
            term=annotation['code']['term'],
            description=annotation['code']['description'],
            type_id=annotation['code']['type_id'],
            reference=annotation['code']['reference'],
            coordinates=annotation['code']['coordinates'],
            project_id=annotation['code']['project_id'],
            code_type=None
        ) if annotation['code'] else None
    ) for annotation in annotations]

@router.get("/annotations/{annotation_id}", response_model=AnnotationResponse)
def read_annotation(
    annotation_id: int,
    db_manager: DatabaseManager = Depends(get_db)
) -> AnnotationResponse:
    annotation = db_manager.read_annotation(annotation_id)
    if annotation is None:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return AnnotationResponse(
        id=annotation.annotation_id,
        element_id=annotation.element_id,
        code_id=annotation.code_id,
        project_id=annotation.project_id,
        code=CodeResponse(
            id=annotation.code.code_id,
            code_id=annotation.code.code_id,
            term=annotation.code.term,
            description=annotation.code.description,
            type_id=annotation.code.type_id,
            reference=annotation.code.reference,
            coordinates=annotation.code.coordinates,
            project_id=annotation.code.project_id,
            code_type=CodeTypeResponse(
                id=annotation.code.code_type.type_id,
                type_id=annotation.code.code_type.type_id,
                type_name=annotation.code.code_type.type_name,
                project_id=annotation.code.code_type.project_id
            ) if annotation.code.code_type else None
        ) if annotation.code else None
    )

@router.put("/annotations/{annotation_id}", response_model=AnnotationResponse)
def update_annotation(
    annotation_id: int,
    annotation: AnnotationUpdate,
    db_manager: DatabaseManager = Depends(get_db)
) -> AnnotationResponse:
    updated_annotation = db_manager.update_annotation(annotation_id, annotation.element_id, annotation.code_id)
    if updated_annotation is None:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    # Convert the Annotation object to a dictionary
    annotation_dict = {
        "id": updated_annotation.annotation_id,
        "element_id": updated_annotation.element_id,
        "code_id": updated_annotation.code_id,
        "project_id": updated_annotation.project_id,
        "code": {
            "id": updated_annotation.code.code_id,
            "code_id": updated_annotation.code.code_id,
            "term": updated_annotation.code.term,
            "description": updated_annotation.code.description,
            "type_id": updated_annotation.code.type_id,
            "reference": updated_annotation.code.reference,
            "coordinates": updated_annotation.code.coordinates,
            "project_id": updated_annotation.code.project_id,
            "code_type": None  # Assuming code_type is not needed in this context
        } if updated_annotation.code else None
    }
    
    return AnnotationResponse.model_validate(annotation_dict)

@router.delete("/annotations/{annotation_id}")
def delete_annotation(
    annotation_id: int,
    db_manager: DatabaseManager = Depends(get_db)
):
    db_manager.delete_annotation(annotation_id)
    return {"message": "Annotation deleted successfully"}


# Additional endpoints
@router.post("/merge_codes/")
def merge_codes(
    code_a_id: int,
    code_b_id: int,
    db_manager: DatabaseManager = Depends(get_db)
):
    try:
        code_a = db_manager.read_code(code_a_id)
        code_b = db_manager.read_code(code_b_id)
        if code_a is None or code_b is None:
            raise HTTPException(status_code=404, detail="One or both codes not found")
        
        merged_code = db_manager.merge_codes(code_a_id, code_b_id)
        if merged_code is None:
            raise HTTPException(status_code=400, detail="Failed to merge codes")
        return {"message": f"Successfully merged Code {code_a_id} into Code {code_b_id}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/annotations_for_code/{code_id}", response_model=List[AnnotationResponse])
def get_annotations_for_code(
    code_id: int,
    db_manager: DatabaseManager = Depends(get_db)
) -> List[AnnotationResponse]:
    annotations = db_manager.get_annotations_for_code(code_id)
    return [AnnotationResponse.model_validate(annotation) for annotation in annotations]

@router.get("/search_elements/", response_model=List[ElementResponse])
def search_elements(
    response: Response,
    search_term: str = Query("", min_length=0),
    series_ids: Optional[str] = Query(None),
    segment_ids: Optional[str] = Query(None),
    code_ids: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db_manager: DatabaseManager = Depends(get_db)
) -> List[ElementResponse]:
    series_id_list = [int(id) for id in series_ids.split(",")] if series_ids else []
    segment_id_list = [int(id) for id in segment_ids.split(",")] if segment_ids else []
    code_id_list = [int(id) for id in code_ids.split(",")] if code_ids else []

    elements = db_manager.search_elements(
        search_term, series_id_list, segment_id_list, code_id_list, skip, limit
    )
    if elements is None:
        raise HTTPException(status_code=500, detail="Error searching elements")
        
    # Get total count for pagination
    total_count = db_manager.count_elements(search_term, series_id_list, segment_id_list, code_id_list)
        
    # Add pagination headers
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["X-Limit"] = str(limit)
    response.headers["X-Skip"] = str(skip)
        
    # Convert SQLAlchemy model instances to Pydantic models
    return [ElementResponse(
        id=element.element_id,
        element_text=element.element_text,
        segment_id=element.segment_id,
        project_id=element.project_id,
        segment=SegmentResponse(
            id=element.segment.segment_id,
            segment_id=element.segment.segment_id,
            segment_title=element.segment.segment_title,
            series_id=element.segment.series_id,
            project_id=element.segment.project_id,
            series=None
        ) if element.segment else None,
        annotations=[]
    ) for element in elements]

# APP SETUP

def create_app(database_url: str | None = None):
    app = FastAPI()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8080", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def get_db_for_request():
        return get_db(database_url)

    app.dependency_overrides[get_db] = get_db_for_request
        
    app.include_router(router)

    return app

app = create_app()

# This function is no longer needed as create_app can handle both cases
# def create_test_app(database_url: str):
#     return create_app(database_url)

if __name__ == "__main__":
    import uvicorn  # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)
