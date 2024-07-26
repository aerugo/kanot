"""
This type stub file was generated by pyright.
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import FastAPI, Response
from pydantic import BaseModel
from .db.crud import DatabaseManager

log_config = ...
logger = ...
class ProjectBase(BaseModel):
    project_title: str
    project_description: str | None = ...


class ProjectCreate(ProjectBase):
    ...


class ProjectUpdate(BaseModel):
    project_title: str | None = ...
    project_description: str | None = ...


class ProjectResponse(ProjectBase):
    project_id: int
    model_config = ...


class CodeTypeBase(BaseModel):
    type_id: int
    project_id: int
    ...


class CodeTypeCreate(BaseModel):
    type_name: str
    project_id: int
    ...


class CodeTypeUpdate(BaseModel):
    type_name: Optional[str] = ...


class CodeBase(BaseModel):
    term: str
    description: str
    type_id: int
    reference: str
    coordinates: str
    project_id: int
    ...


class CodeCreate(CodeBase):
    ...


class CodeUpdate(BaseModel):
    term: Optional[str] = ...
    description: Optional[str] = ...
    type_id: Optional[int] = ...
    reference: Optional[str] = ...
    coordinates: Optional[str] = ...


class SeriesBase(BaseModel):
    series_id: int
    series_title: str
    project_id: int
    ...


class SeriesCreate(BaseModel):
    series_title: str
    project_id: int
    ...


class SeriesUpdate(BaseModel):
    series_title: Optional[str] = ...


class SegmentBase(BaseModel):
    segment_id: int
    segment_title: str
    series_id: int
    project_id: int
    ...


class SegmentCreate(BaseModel):
    segment_title: str
    series_id: int
    project_id: int
    ...


class SegmentUpdate(BaseModel):
    segment_title: Optional[str] = ...


class ElementBase(BaseModel):
    element_text: str
    segment_id: int
    project_id: int
    ...


class ElementCreate(ElementBase):
    ...


class ElementUpdate(BaseModel):
    element_text: Optional[str] = ...
    segment_id: Optional[int] = ...


class ElementResponse(BaseModel):
    element_id: int
    element_text: Optional[str] = ...
    segment_id: int
    project_id: int
    segment: Optional[SegmentResponse] = ...
    annotations: List[AnnotationResponseNoElement] = ...
    model_config = ...


class SegmentResponse(BaseModel):
    segment_id: int
    segment_title: str
    series_id: int
    project_id: int
    series: Optional[SeriesResponse] = ...
    model_config = ...


class SeriesResponse(BaseModel):
    series_id: int
    series_title: str
    project_id: int
    model_config = ...


class CodeTypeResponse(BaseModel):
    type_id: int
    type_name: str
    project_id: int
    model_config = ...


class CodeResponse(BaseModel):
    code_id: int
    term: str
    description: Optional[str] = ...
    type_id: Optional[int] = ...
    code_type: Optional[CodeTypeResponse] = ...
    reference: Optional[str] = ...
    coordinates: Optional[str] = ...
    project_id: int
    model_config = ...


class AnnotationResponseNoElement(BaseModel):
    annotation_id: int
    code: Optional[CodeResponse] = ...
    model_config = ...


class AnnotationBase(BaseModel):
    element_id: int
    code_id: int
    project_id: int
    ...


class AnnotationCreate(AnnotationBase):
    ...


class BatchAnnotationCreate(BaseModel):
    project_id: int
    element_ids: List[int]
    code_ids: List[int]
    ...


class BatchAnnotationRemove(BaseModel):
    element_ids: List[int]
    code_ids: List[int]
    ...


class AnnotationUpdate(BaseModel):
    element_id: Optional[int] = ...
    code_id: Optional[int] = ...


class AnnotationResponse(BaseModel):
    annotation_id: int
    element_id: int
    code_id: int
    code: Optional[CodeResponse]
    model_config = ...


def configure_database(database_url: str | None = ...): # -> DatabaseManager:
    ...

def get_db(database_url: str | None = ...): # -> DatabaseManager:
    ...

router = ...
@router.post("/projects/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db_manager: DatabaseManager = ...) -> ProjectResponse:
    ...

@router.get("/projects/", response_model=List[ProjectResponse])
def read_projects(db_manager: DatabaseManager = ...) -> List[ProjectResponse]:
    ...

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def read_project(project_id: int, db_manager: DatabaseManager = ...) -> ProjectResponse:
    ...

@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectUpdate, db_manager: DatabaseManager = ...) -> ProjectResponse:
    ...

@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db_manager: DatabaseManager = ...): # -> dict[str, str]:
    ...

@router.post("/code_types/", response_model=CodeTypeResponse)
def create_code_type(code_type: CodeTypeCreate, db_manager: DatabaseManager = ...) -> CodeTypeResponse:
    ...

@router.get("/code_types/", response_model=List[CodeTypeResponse])
def read_code_types(db_manager: DatabaseManager = ...) -> List[CodeTypeResponse]:
    ...

@router.get("/code_types/{type_id}", response_model=CodeTypeResponse)
def read_code_type(type_id: int, db_manager: DatabaseManager = ...) -> CodeTypeResponse:
    ...

@router.put("/code_types/{type_id}", response_model=CodeTypeResponse)
def update_code_type(type_id: int, code_type: CodeTypeCreate, db_manager: DatabaseManager = ...) -> CodeTypeResponse:
    ...

@router.delete("/code_types/{type_id}")
def delete_code_type(type_id: int, db_manager: DatabaseManager = ...): # -> dict[str, str]:
    ...

@router.post("/codes/", response_model=CodeResponse)
def create_code(code: CodeCreate, db_manager: DatabaseManager = ...) -> CodeResponse:
    ...

@router.get("/codes/", response_model=List[CodeResponse])
def read_codes(db_manager: DatabaseManager = ...) -> List[CodeResponse]:
    ...

@router.get("/codes/{code_id}", response_model=CodeResponse)
def read_code(code_id: int, db_manager: DatabaseManager = ...) -> CodeResponse:
    ...

@router.put("/codes/{code_id}", response_model=CodeResponse)
def update_code(code_id: int, code: CodeUpdate, db_manager: DatabaseManager = ...) -> CodeResponse:
    ...

@router.delete("/codes/{code_id}")
def delete_code(code_id: int, db_manager: DatabaseManager = ...): # -> dict[str, str]:
    ...

@router.post("/series/", response_model=SeriesResponse)
def create_series(series: SeriesCreate, db_manager: DatabaseManager = ...) -> SeriesResponse:
    ...

@router.get("/series/", response_model=List[SeriesResponse])
def read_all_series(db_manager: DatabaseManager = ...) -> List[SeriesResponse]:
    ...

@router.get("/series/{series_id}", response_model=SeriesResponse)
def read_series(series_id: int, db_manager: DatabaseManager = ...) -> SeriesResponse:
    ...

@router.put("/series/{series_id}", response_model=SeriesResponse)
def update_series(series_id: int, series: SeriesUpdate, db_manager: DatabaseManager = ...) -> SeriesResponse:
    ...

@router.delete("/series/{series_id}")
def delete_series(series_id: int, db_manager: DatabaseManager = ...): # -> dict[str, str]:
    ...

@router.post("/segments/", response_model=SegmentResponse)
def create_segment(segment: SegmentCreate, db_manager: DatabaseManager = ...) -> SegmentResponse:
    ...

@router.get("/segments/", response_model=List[SegmentResponse])
def read_segments(db_manager: DatabaseManager = ...) -> List[SegmentResponse]:
    ...

@router.get("/segments/{segment_id}", response_model=SegmentResponse)
def read_segment(segment_id: int, db_manager: DatabaseManager = ...) -> SegmentResponse:
    ...

@router.put("/segments/{segment_id}", response_model=SegmentResponse)
def update_segment(segment_id: int, segment: SegmentUpdate, db_manager: DatabaseManager = ...) -> SegmentResponse:
    ...

@router.delete("/segments/{segment_id}")
def delete_segment(segment_id: int, db_manager: DatabaseManager = ...): # -> dict[str, str]:
    ...

@router.post("/elements/", response_model=ElementResponse)
def create_element(element: ElementCreate, db_manager: DatabaseManager = ...) -> ElementResponse:
    ...

@router.get("/elements/", response_model=List[ElementResponse])
def read_elements(skip: int = ..., limit: int = ..., db_manager: DatabaseManager = ...) -> List[ElementResponse]:
    ...

@router.get("/elements/{element_id}", response_model=ElementResponse)
def read_element(element_id: int, db_manager: DatabaseManager = ...) -> ElementResponse:
    ...

@router.put("/elements/{element_id}", response_model=ElementResponse)
def update_element(element_id: int, element: ElementUpdate, db_manager: DatabaseManager = ...) -> ElementResponse:
    ...

@router.delete("/elements/{element_id}")
def delete_element(element_id: int, db_manager: DatabaseManager = ...): # -> dict[str, str]:
    ...

@router.post("/annotations/", response_model=AnnotationResponse)
def create_annotation(annotation: AnnotationCreate, db_manager: DatabaseManager = ...) -> AnnotationResponse:
    ...

@router.post("/batch_annotations/", response_model=List[AnnotationResponse])
def create_batch_annotations(batch_data: BatchAnnotationCreate, db_manager: DatabaseManager = ...) -> List[AnnotationResponse]:
    ...

@router.delete("/batch_annotations/", response_model=List[AnnotationResponse])
def remove_batch_annotations(batch_data: BatchAnnotationRemove, db_manager: DatabaseManager = ...) -> List[AnnotationResponse]:
    ...

@router.get("/annotations/", response_model=List[AnnotationResponse])
def read_annotations(db_manager: DatabaseManager = ...) -> List[AnnotationResponse]:
    ...

@router.get("/annotations/{annotation_id}", response_model=AnnotationResponse)
def read_annotation(annotation_id: int, db_manager: DatabaseManager = ...) -> AnnotationResponse:
    ...

@router.put("/annotations/{annotation_id}", response_model=AnnotationResponse)
def update_annotation(annotation_id: int, annotation: AnnotationUpdate, db_manager: DatabaseManager = ...) -> AnnotationResponse:
    ...

@router.delete("/annotations/{annotation_id}")
def delete_annotation(annotation_id: int, db_manager: DatabaseManager = ...): # -> dict[str, str]:
    ...

@router.post("/merge_codes/")
def merge_codes(code_a_id: int, code_b_id: int, db_manager: DatabaseManager = ...): # -> dict[str, str]:
    ...

@router.get("/annotations_for_code/{code_id}", response_model=List[AnnotationResponse])
def get_annotations_for_code(code_id: int, db_manager: DatabaseManager = ...) -> List[AnnotationResponse]:
    ...

@router.get("/search_elements/", response_model=List[ElementResponse])
def search_elements(response: Response, search_term: str = ..., series_ids: Optional[str] = ..., segment_ids: Optional[str] = ..., code_ids: Optional[str] = ..., skip: int = ..., limit: int = ..., db_manager: DatabaseManager = ...) -> List[ElementResponse]:
    ...

def create_app(database_url: str | None = ..., db_session: DatabaseManager | None = ...) -> FastAPI:
    ...

app = ...
if __name__ == "__main__":
    ...
