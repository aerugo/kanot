from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')

class ProjectRelatedModel(BaseModel):
    project_id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class CreateModel(BaseModel, Generic[T]):
    pass

class UpdateModel(BaseModel, Generic[T]):
    pass

class ResponseModel(BaseModel, Generic[T]):
    id: int
    project_id: int

class ProjectBase(BaseModel):
    project_title: str
    project_description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    project_title: Optional[str] = None
    project_description: Optional[str] = None

class ProjectResponse(ResponseModel[ProjectBase], ProjectBase):
    pass

class CodeTypeBase(BaseModel):
    type_name: str
    project_id: int

class CodeTypeCreate(CodeTypeBase):
    pass

class CodeTypeUpdate(BaseModel):
    type_name: Optional[str] = None

class CodeTypeResponse(ResponseModel[CodeTypeBase], CodeTypeBase):
    type_id: int

class CodeBase(BaseModel):
    term: str
    description: Optional[str] = None
    type_id: int
    reference: Optional[str] = None
    coordinates: Optional[str] = None
    project_id: int

class CodeCreate(CodeBase):
    pass

class CodeUpdate(BaseModel):
    term: Optional[str] = None
    description: Optional[str] = None
    type_id: Optional[int] = None
    reference: Optional[str] = None
    coordinates: Optional[str] = None

class CodeResponse(ResponseModel[CodeBase], CodeBase):
    code_id: int
    code_type: Optional[CodeTypeResponse] = None

class SeriesBase(BaseModel):
    series_title: str
    project_id: int

class SeriesCreate(SeriesBase):
    pass

class SeriesUpdate(BaseModel):
    series_title: Optional[str] = None

class SeriesResponse(ResponseModel[SeriesBase], SeriesBase):
    series_id: int

class SegmentBase(BaseModel):
    segment_title: str
    series_id: int
    project_id: int

class SegmentCreate(SegmentBase):
    pass

class SegmentUpdate(BaseModel):
    segment_title: Optional[str] = None

class SegmentResponse(ResponseModel[SegmentBase], SegmentBase):
    segment_id: int
    series: Optional[SeriesResponse] = None

class ElementBase(BaseModel):
    element_text: str
    segment_id: int
    project_id: int

class ElementCreate(ElementBase):
    pass

class ElementUpdate(BaseModel):
    element_text: Optional[str] = None
    segment_id: Optional[int] = None

class AnnotationResponseMinimal(BaseModel):
    annotation_id: int
    code: Optional[CodeResponse] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ElementResponse(ResponseModel[ElementBase], ElementBase):
    segment: Optional[SegmentResponse] = None
    annotations: List[AnnotationResponseMinimal] = []

class AnnotationBase(BaseModel):
    element_id: int
    code_id: int
    project_id: int

class AnnotationCreate(AnnotationBase):
    pass

class AnnotationUpdate(BaseModel):
    element_id: Optional[int] = None
    code_id: Optional[int] = None

class AnnotationResponse(ResponseModel[AnnotationBase], AnnotationBase):
    code: Optional[CodeResponse] = None

class BatchAnnotationCreate(BaseModel):
    element_ids: List[int]
    code_ids: List[int]
    project_id: int

class BatchAnnotationRemove(BaseModel):
    element_ids: List[int]
    code_ids: List[int]
