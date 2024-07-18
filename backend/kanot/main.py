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
    allow_origins=["http://localhost:8080"],
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
class CodeTypeBase(BaseModel):
    type_id: int

class CodeTypeCreate(CodeTypeBase):
    type_name: str
    pass

class CodeTypeUpdate(BaseModel):
    type_name: Optional[str] = None

class CodeTypeResponse(CodeTypeBase):
    type_id: int
    type_name: str

    class Config:
        from_attributes = True

class CodeBase(BaseModel):
    term: str
    description: str
    type_id: int
    reference: str
    coordinates: str

class CodeCreate(CodeBase):
    pass

class CodeUpdate(BaseModel):
    term: Optional[str] = None
    description: Optional[str] = None
    type_id: Optional[int] = None
    reference: Optional[str] = None
    coordinates: Optional[str] = None

class CodeResponse(BaseModel):
    code_id: int
    term: str
    description: Optional[str] = None
    type_id: Optional[int] = None
    code_type: Optional[CodeTypeResponse]
    reference: Optional[str] = None
    coordinates: Optional[str] = None

    class Config:
        from_attributes = True

class SeriesBase(BaseModel):
    series_id: int
    series_title: str

class SeriesCreate(SeriesBase):
    pass

class SeriesUpdate(BaseModel):
    series_title: Optional[str] = ""

class SeriesResponse(BaseModel):
    series_id: int
    series_title: str

    class Config:
        from_attributes = True
        orm_mode = True

class SegmentBase(BaseModel):
    segment_id: int
    segment_title: str
    series_id: int

class SegmentCreate(SegmentBase):
    pass

class SegmentUpdate(BaseModel):
    segment_title: Optional[str] = None

class SegmentResponse(BaseModel):
    segment_id: int
    segment_title: str
    series: Optional[SeriesResponse] = None

    class Config:
        from_attributes = True
        orm_mode = True

class ElementBase(BaseModel):
    element_text: str
    segment_id: int

class ElementCreate(ElementBase):
    pass

class ElementUpdate(BaseModel):
    element_text: Optional[str] = None
    segment_id: Optional[int] = None

class ElementResponse(BaseModel):
    element_id: int
    element_text: Optional[str] = None
    segment: Optional[SegmentResponse] = None
    annotations: List[AnnotationResponseNoElement] = []

    class Config:
        from_attributes = True
        orm_mode = True

class AnnotationResponseNoElement(BaseModel):
    annotation_id: int
    code: Optional[CodeResponse] = None

    class Config:
        from_attributes = True
        orm_mode = True

class AnnotationBase(BaseModel):
    element_id: int
    code_id: int

class AnnotationCreate(AnnotationBase):
    pass

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
        orm_mode = True
        
# API endpoints

# CodeType endpoints
@app.post("/code_types/", response_model=CodeTypeResponse)
def create_code_type(code_type: CodeTypeCreate, db: Session = Depends(get_db)):
    new_code_type = db_manager.create_code_type(code_type.type_name)
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
        new_code = db_manager.create_code(code.term, code.description, code.type_id, code.reference, code.coordinates)
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
    new_series = db_manager.create_series(series.series_title)
    return new_series

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
    new_segment = db_manager.create_segment(segment.segment_id, segment.segment_title)
    return new_segment

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
    new_element = db_manager.create_element(element.element_text, element.segment_id)
    return new_element

@app.get("/elements/", response_model=List[ElementResponse])
def read_elements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    elements = db_manager.read_elements_paginated(skip=skip, limit=limit)
    return elements

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
    new_annotation = db_manager.create_annotation(annotation.element_id, annotation.code_id)
    if new_annotation is None:
        raise HTTPException(status_code=400, detail="Failed to create annotation")
    return new_annotation

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
):
    logger.info(f"Received search request - series_ids: {series_ids}, segment_ids: {segment_ids}, code_ids: {code_ids}")
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
    
    return elements


if __name__ == "__main__":
    import uvicorn  # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)