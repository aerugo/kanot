from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

class Config:
    from_attributes = True
    populate_by_name = True

class ProjectRelatedModel(BaseModel):
    project_id: int

    class Config(Config):
        pass

class CreateModel(Generic[T]):
    pass

class UpdateModel(Generic[T]):
    pass

class ResponseModel(Generic[T], ProjectRelatedModel):
    id: int

class ProjectBase(BaseModel):
    project_title: str
    project_description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    project_title: Optional[str] = None
    project_description: Optional[str] = None

class ProjectResponse(ProjectBase, ResponseModel[ProjectBase]):
    pass

class CodeTypeBase(ProjectRelatedModel):
    type_name: str

class CodeTypeCreate(CodeTypeBase):
    pass

class CodeTypeUpdate(BaseModel):
    type_name: Optional[str] = None

class CodeTypeResponse(CodeTypeBase, ResponseModel[CodeTypeBase]):
    pass

class CodeBase(ProjectRelatedModel):
    term: str
    description: Optional[str] = None
    type_id: int
    reference: Optional[str] = None
    coordinates: Optional[str] = None

class CodeCreate(CodeBase):
    pass

class CodeUpdate(BaseModel):
    term: Optional[str] = None
    description: Optional[str] = None
    type_id: Optional[int] = None
    reference: Optional[str] = None
    coordinates: Optional[str] = None

class CodeResponse(CodeBase, ResponseModel[CodeBase]):
    code_type: Optional[CodeTypeResponse] = None

class SeriesBase(ProjectRelatedModel):
    series_title: str

class SeriesCreate(SeriesBase):
    pass

class SeriesUpdate(BaseModel):
    series_title: Optional[str] = None

class SeriesResponse(SeriesBase, ResponseModel[SeriesBase]):
    pass

class SegmentBase(ProjectRelatedModel):
    segment_title: str
    series_id: int

class SegmentCreate(SegmentBase):
    pass

class SegmentUpdate(BaseModel):
    segment_title: Optional[str] = None

class SegmentResponse(SegmentBase, ResponseModel[SegmentBase]):
    series: Optional[SeriesResponse] = None

class ElementBase(ProjectRelatedModel):
    element_text: str
    segment_id: int

class ElementCreate(ElementBase):
    pass

class ElementUpdate(BaseModel):
    element_text: Optional[str] = None
    segment_id: Optional[int] = None

class AnnotationResponseMinimal(BaseModel):
    annotation_id: int
    code: Optional[CodeResponse] = None

    class Config(Config):
        pass

class ElementResponse(ElementBase, ResponseModel[ElementBase]):
    segment: Optional[SegmentResponse] = None
    annotations: List[AnnotationResponseMinimal] = []

class AnnotationBase(ProjectRelatedModel):
    element_id: int
    code_id: int

class AnnotationCreate(AnnotationBase):
    pass

class AnnotationUpdate(BaseModel):
    element_id: Optional[int] = None
    code_id: Optional[int] = None

class AnnotationResponse(AnnotationBase, ResponseModel[AnnotationBase]):
    code: Optional[CodeResponse] = None

class BatchAnnotationCreate(ProjectRelatedModel):
    element_ids: List[int]
    code_ids: List[int]

class BatchAnnotationRemove(BaseModel):
    element_ids: List[int]
    code_ids: List[int]
