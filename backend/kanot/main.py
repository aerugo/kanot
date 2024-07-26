from __future__ import annotations

import logging
import traceback
from logging.config import dictConfig
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db.crud import DatabaseManager

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

# Create FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database engine
DATABASE_URL = "sqlite:///local_database.db"
from pathlib import Path

logger.info(f"Local sqlite database on : {Path(DATABASE_URL).resolve()}")

engine = create_engine(DATABASE_URL)

# Create DatabaseManager instance
db_manager = DatabaseManager(engine)

# Dependency to get database session
def get_db():
    session = db_manager.Session()
    try:
        yield session
    finally:
        session.close()

# Pydantic models
class ProjectBase(BaseModel):
    project_title: str
    project_description: str | None = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    project_title: str | None = None
    project_description: str | None = None

class ProjectResponse(ProjectBase):
    project_id: int

    class Config:
        from_attributes = True

class CodeTypeBase(BaseModel):
    type_id: int
    project_id: int

class CodeTypeCreate(BaseModel):
    type_name: str
    project_id: int

class CodeTypeUpdate(BaseModel):
    type_name: Optional[str] = None

class CodeBase(BaseModel):
    term: str
    description: str
    type_id: int
    reference: str
    coordinates: str
    project_id: int

class CodeCreate(CodeBase):
    pass

class CodeUpdate(BaseModel):
    term: Optional[str] = None
    description: Optional[str] = None
    type_id: Optional[int] = None
    reference: Optional[str] = None
    coordinates: Optional[str] = None

class SeriesBase(BaseModel):
    series_id: int
    series_title: str
    project_id: int

class SeriesCreate(BaseModel):
    series_title: str
    project_id: int

class SeriesUpdate(BaseModel):
    series_title: Optional[str] = ""

class SegmentBase(BaseModel):
    segment_id: int
    segment_title: str
    series_id: int
    project_id: int

class SegmentCreate(BaseModel):
    segment_title: str
    series_id: int
    project_id: int

class SegmentUpdate(BaseModel):
    segment_title: Optional[str] = None

class ElementBase(BaseModel):
    element_text: str
    segment_id: int
    project_id: int

class ElementCreate(ElementBase):
    pass

class ElementUpdate(BaseModel):
    element_text: Optional[str] = None
    segment_id: Optional[int] = None

class ElementResponse(BaseModel):
    element_id: int
    element_text: Optional[str] = None
    segment_id: int
    project_id: int
    segment: Optional[SegmentResponse] = None
    annotations: List[AnnotationResponseNoElement] = []

    class Config:
        from_attributes = True
        populate_by_name = True

class SegmentResponse(BaseModel):
    segment_id: int
    segment_title: str
    series_id: int
    project_id: int
    series: Optional[SeriesResponse] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class SeriesResponse(BaseModel):
    series_id: int
    series_title: str
    project_id: int

    class Config:
        from_attributes = True
        populate_by_name = True

class CodeTypeResponse(BaseModel):
    type_id: int
    type_name: str
    project_id: int

    class Config:
        from_attributes = True
        populate_by_name = True

class CodeResponse(BaseModel):
    code_id: int
    term: str
    description: Optional[str] = None
    type_id: Optional[int] = None
    code_type: Optional[CodeTypeResponse] = None
    reference: Optional[str] = None
    coordinates: Optional[str] = None
    project_id: int

    class Config:
        from_attributes = True
        populate_by_name = True

class AnnotationResponseNoElement(BaseModel):
    annotation_id: int
    code: Optional[CodeResponse] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class AnnotationBase(BaseModel):
    element_id: int
    code_id: int
    project_id: int

class AnnotationCreate(AnnotationBase):
    pass

class BatchAnnotationCreate(BaseModel):
    project_id: int
    element_ids: List[int]
    code_ids: List[int]

class BatchAnnotationRemove(BaseModel):
    element_ids: List[int]
    code_ids: List[int]

class AnnotationUpdate(BaseModel):
    element_id: Optional[int] = None
    code_id: Optional[int] = None

class AnnotationResponse(BaseModel):
    annotation_id: int
    element_id: int
    code_id: int
    code: Optional[CodeResponse]

    class Config:
        from_attributes = True
        
# API endpoints

# Project endpoints
@app.post("/projects/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    new_project = db_manager.create_project(project.project_title, project.project_description)
    return new_project

@app.get("/projects/", response_model=List[ProjectResponse])
def read_projects(db: Session = Depends(get_db)):
    projects = db_manager.read_all_projects()
    return projects

@app.get("/projects/{project_id}", response_model=ProjectResponse)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = db_manager.read_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    db_manager.update_project(project_id, project.project_title, project.project_description)
    updated_project = db_manager.read_project(project_id)
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_manager.delete_project(project_id)
    return {"message": "Project deleted successfully"}

# CodeType endpoints
@app.post("/code_types/", response_model=CodeTypeResponse)
def create_code_type(code_type: CodeTypeCreate, db: Session = Depends(get_db)):
    new_code_type = db_manager.create_code_type(code_type.type_name, code_type.project_id)
    if new_code_type is None:
        raise HTTPException(status_code=400, detail=f"Code type '{code_type.type_name}' already exists in this project")
    return new_code_type

@app.get("/code_types/", response_model=List[CodeTypeResponse])
def read_code_types(db: Session = Depends(get_db)):
    code_types = db_manager.read_all_code_types()
    return code_types

@app.get("/code_types/{type_id}", response_model=CodeTypeResponse)
def read_code_type(type_id: int, db: Session = Depends(get_db)):
    code_type = db_manager.read_code_type(type_id)
    if code_type is None:
        raise HTTPException(status_code=404, detail="Code type not found")
    return code_type

@app.put("/code_types/{type_id}", response_model=CodeTypeResponse)
def update_code_type(type_id: int, code_type: CodeTypeCreate, db: Session = Depends(get_db)):
    db_manager.update_code_type(type_id, code_type.type_name)
    updated_code_type = db_manager.read_code_type(type_id)
    if updated_code_type is None:
        raise HTTPException(status_code=404, detail="Code type not found")
    return updated_code_type

@app.delete("/code_types/{type_id}")
def delete_code_type(type_id: int, db: Session = Depends(get_db)):
    db_manager.delete_code_type(type_id)
    return {"message": "Code type deleted successfully"}

# Code endpoints
@app.post("/codes/", response_model=CodeResponse)
def create_code(code: CodeCreate, db: Session = Depends(get_db)):
    try:
        new_code = db_manager.create_code(code.term, code.description, code.type_id, code.reference, code.coordinates, code.project_id)
        if new_code is None:
            return JSONResponse(
                status_code=400,
                content={"message": "Code with this term already exists"}
            )
        
        # Log the new_code object
        logger.info(f"New code created: {new_code}")
        
        # Try to serialize the response
        json_compatible_item_data = jsonable_encoder(new_code)
        logger.info(f"Serialized code: {json_compatible_item_data}")
        
        return JSONResponse(content=json_compatible_item_data)
    except IntegrityError as e:
        logger.error(f"IntegrityError when creating code: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"message": "Code with this term already exists"}
        )
    except Exception as e:
        logger.error(f"Unexpected error when creating code: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"message": "An unexpected error occurred"}
        )

@app.get("/codes/", response_model=List[CodeResponse])
def read_codes(db: Session = Depends(get_db)):
    codes = db_manager.read_all_codes()
    return codes

@app.get("/codes/{code_id}", response_model=CodeResponse)
def read_code(code_id: int, db: Session = Depends(get_db)):
    code = db_manager.read_code(code_id)
    if code is None:
        raise HTTPException(status_code=404, detail="Code not found")
    return code

@app.put("/codes/{code_id}", response_model=CodeResponse)
def update_code(code_id: int, code: CodeUpdate, db: Session = Depends(get_db)):
    db_manager.update_code(code_id, code.term, code.description, code.type_id, code.reference, code.coordinates)
    updated_code = db_manager.read_code(code_id)
    if updated_code is None:
        raise HTTPException(status_code=404, detail="Code not found")
    return updated_code

@app.delete("/codes/{code_id}")
def delete_code(code_id: int, db: Session = Depends(get_db)):
    db_manager.delete_code(code_id)
    return {"message": "Code deleted successfully"}

# Series endpoints
@app.post("/series/", response_model=SeriesResponse)
def create_series(series: SeriesCreate, db: Session = Depends(get_db)):
    new_series = db_manager.create_series(series.series_title, series.project_id)
    if new_series is None:
        raise HTTPException(status_code=400, detail="Failed to create series")
    return SeriesResponse(
        series_id=new_series.series_id,
        series_title=new_series.series_title,
        project_id=new_series.project_id
    )

@app.get("/series/", response_model=List[SeriesResponse])
def read_all_series(db: Session = Depends(get_db)):
    series = db_manager.read_all_series()
    return series

@app.get("/series/{series_id}", response_model=SeriesResponse)
def read_series(series_id: int, db: Session = Depends(get_db)):
    series = db_manager.read_series(series_id)
    if series is None:
        raise HTTPException(status_code=404, detail="Series not found")
    return series

@app.put("/series/{series_id}", response_model=SeriesResponse)
def update_series(series_id: int, series: SeriesUpdate, db: Session = Depends(get_db)):
    db_manager.update_series(series_id, series.series_title)
    updated_series = db_manager.read_series(series_id)
    if updated_series is None:
        raise HTTPException(status_code=404, detail="Series not found")
    return updated_series

@app.delete("/series/{series_id}")
def delete_series(series_id: int, db: Session = Depends(get_db)):
    db_manager.delete_series(series_id)
    return {"message": "Series deleted successfully"}

# Segment endpoints
@app.post("/segments/", response_model=SegmentResponse)
def create_segment(segment: SegmentCreate, db: Session = Depends(get_db)):
    new_segment = db_manager.create_segment(segment.segment_title, segment.series_id, segment.project_id)
    if new_segment is None:
        raise HTTPException(status_code=400, detail="Failed to create segment")
    return SegmentResponse(
        segment_id=new_segment.segment_id,
        segment_title=new_segment.segment_title,
        series_id=new_segment.series_id,
        project_id=new_segment.project_id
    )

@app.get("/segments/", response_model=List[SegmentResponse])
def read_segments(db: Session = Depends(get_db)):
    segments = db_manager.read_all_segments()
    return segments

@app.get("/segments/{segment_id}", response_model=SegmentResponse)
def read_segment(segment_id: int, db: Session = Depends(get_db)):
    segment = db_manager.read_segment(segment_id)
    if segment is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment

@app.put("/segments/{segment_id}", response_model=SegmentResponse)
def update_segment(segment_id: int, segment: SegmentUpdate, db: Session = Depends(get_db)):
    db_manager.update_segment(segment_id, segment.segment_title)
    updated_segment = db_manager.read_segment(segment_id)
    if updated_segment is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    return updated_segment

@app.delete("/segments/{segment_id}")
def delete_segment(segment_id: int, db: Session = Depends(get_db)):
    db_manager.delete_segment(segment_id)
    return {"message": "Segment deleted successfully"}

# Element endpoints
@app.post("/elements/", response_model=ElementResponse)
def create_element(element: ElementCreate, db: Session = Depends(get_db)):
    new_element = db_manager.create_element(element.element_text, element.segment_id, element.project_id)
    assert new_element is not None
    return ElementResponse(
        element_id=new_element.element_id,
        element_text=new_element.element_text,
        segment_id=new_element.segment_id,
        project_id=new_element.project_id,
        segment=SegmentResponse(
            segment_id=new_element.segment.segment_id,
            segment_title=new_element.segment.segment_title,
            series_id=new_element.segment.series_id,
            project_id=new_element.segment.project_id
        ) if new_element.segment else None,
        annotations=[]
    )

@app.get("/elements/", response_model=List[ElementResponse])
def read_elements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    elements = db_manager.read_elements_paginated(skip=skip, limit=limit)
    assert elements is not None
    return [
        ElementResponse(
            element_id=element.element_id,
            element_text=element.element_text,
            segment_id=element.segment_id,
            project_id=element.project_id,
            segment=SegmentResponse(
                segment_id=element.segment.segment_id,
                segment_title=element.segment.segment_title,
                series_id=element.segment.series_id,
                project_id=element.segment.project_id
            ) if element.segment else None,
            annotations=[]
        ) for element in elements
    ]

@app.get("/elements/{element_id}", response_model=ElementResponse)
def read_element(element_id: int, db: Session = Depends(get_db)):
    element = db_manager.read_element(element_id)
    if element is None:
        raise HTTPException(status_code=404, detail="Element not found")
    return element

@app.put("/elements/{element_id}", response_model=ElementResponse)
def update_element(element_id: int, element: ElementUpdate, db: Session = Depends(get_db)):
    db_manager.update_element(element_id, element.element_text, element.segment_id)
    updated_element = db_manager.read_element(element_id)
    if updated_element is None:
        raise HTTPException(status_code=404, detail="Element not found")
    return updated_element

@app.delete("/elements/{element_id}")
def delete_element(element_id: int, db: Session = Depends(get_db)):
    db_manager.delete_element(element_id)
    return {"message": "Element deleted successfully"}

# Annotation endpoints
@app.post("/annotations/", response_model=AnnotationResponse)
def create_annotation(annotation: AnnotationCreate, db: Session = Depends(get_db)):
    new_annotation = db_manager.create_annotation(annotation.element_id, annotation.code_id, annotation.project_id)
    if new_annotation is None:
        raise HTTPException(status_code=400, detail="Failed to create annotation")
    return new_annotation

@app.post("/batch_annotations/", response_model=List[AnnotationResponse])
def create_batch_annotations(batch_data: BatchAnnotationCreate, db: Session = Depends(get_db)):
    new_annotations: List[AnnotationResponse] = []
    for element_id in batch_data.element_ids:
        for code_id in batch_data.code_ids:
            annotation = db_manager.create_annotation(element_id, code_id, project_id=batch_data.project_id)
            if annotation:
                new_annotations.append(annotation)
    
    return new_annotations

@app.delete("/batch_annotations/", response_model=List[AnnotationResponse])
def remove_batch_annotations(batch_data: BatchAnnotationRemove, db: Session = Depends(get_db)):
    try:
        removed_annotations: List[AnnotationResponse] = []
        for element_id in batch_data.element_ids:
            for code_id in batch_data.code_ids:
                # Get annotations for the specific element and code
                annotations = db_manager.get_annotations_for_element_and_code(element_id, code_id)
                for annotation in annotations:
                    # Remove the annotation
                    db_manager.delete_annotation(annotation.annotation_id)
                    # Append to the list of removed annotations
                    removed_annotations.append(AnnotationResponse(
                        annotation_id=annotation.annotation_id,
                        element_id=annotation.element_id,
                        code_id=annotation.code_id,
                        code=annotation.code
                    ))
        
        return removed_annotations
    except Exception as e:
        logger.error(f"Error in batch annotation removal: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during batch annotation removal")

@app.get("/annotations/", response_model=List[AnnotationResponse])
def read_annotations(db: Session = Depends(get_db)):
    annotations = db_manager.read_all_annotations()
    return annotations

@app.get("/annotations/{annotation_id}", response_model=AnnotationResponse)
def read_annotation(annotation_id: int, db: Session = Depends(get_db)):
    annotation = db_manager.read_annotation(annotation_id)
    if annotation is None:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotation

@app.put("/annotations/{annotation_id}", response_model=AnnotationResponse)
def update_annotation(annotation_id: int, annotation: AnnotationUpdate, db: Session = Depends(get_db)):
    db_manager.update_annotation(annotation_id, annotation.element_id, annotation.code_id)
    updated_annotation = db_manager.read_annotation(annotation_id)
    if updated_annotation is None:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return updated_annotation

@app.delete("/annotations/{annotation_id}")
def delete_annotation(annotation_id: int, db: Session = Depends(get_db)):
    db_manager.delete_annotation(annotation_id)
    return {"message": "Annotation deleted successfully"}

# Additional endpoints
@app.post("/merge_codes/")
def merge_codes(code_a_id: int, code_b_id: int, db: Session = Depends(get_db)):
    merged_code = db_manager.merge_codes(code_a_id, code_b_id)
    return {"message": f"Successfully merged Code {code_a_id} into Code {code_b_id}: \n {merged_code}"}

@app.get("/annotations_for_code/{code_id}", response_model=List[AnnotationResponse])
def get_annotations_for_code(code_id: int, db: Session = Depends(get_db)):
    annotations = db_manager.get_annotations_for_code(code_id)
    return annotations

@app.get("/search_elements/", response_model=List[ElementResponse])
def search_elements(
    response: Response,
    search_term: str = Query("", min_length=0),
    series_ids: Optional[str] = Query(None),
    segment_ids: Optional[str] = Query(None),
    code_ids: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
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
    elements_responses: List[ElementResponse] = []
    for element in elements:
        element_response = ElementResponse(
            element_id=element.element_id,
            element_text=element.element_text,
            segment_id=element.segment_id,
            project_id=element.project_id,
            segment=SegmentResponse(
                segment_id=element.segment.segment_id,
                segment_title=element.segment.segment_title,
                series_id=element.segment.series_id,
                project_id=element.segment.project_id,
                series=SeriesResponse(
                    series_id=element.segment.series.series_id,
                    series_title=element.segment.series.series_title,
                    project_id=element.segment.series.project_id
                ) if element.segment.series else None
            ) if element.segment else None,
            annotations=[
                AnnotationResponseNoElement(
                    annotation_id=annotation.annotation_id,
                    code=CodeResponse(
                        code_id=annotation.code.code_id,
                        term=annotation.code.term,
                        description=annotation.code.description,
                        type_id=annotation.code.type_id,
                        code_type=CodeTypeResponse(
                            type_id=annotation.code.code_type.type_id,
                            type_name=annotation.code.code_type.type_name,
                            project_id=annotation.code.code_type.project_id
                        ) if annotation.code.code_type else None,
                        reference=annotation.code.reference,
                        coordinates=annotation.code.coordinates,
                        project_id=annotation.code.project_id
                    ) if annotation.code else None
                ) for annotation in element.annotations
            ]
        )
        elements_responses.append(element_response)
    
    return elements_responses


if __name__ == "__main__":
    import uvicorn  # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)
