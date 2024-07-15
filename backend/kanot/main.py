import logging
import traceback
from logging.config import dictConfig
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
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

class EpisodeBase(BaseModel):
    episode_id: str
    episode_title: str

class EpisodeCreate(EpisodeBase):
    pass

class EpisodeUpdate(BaseModel):
    episode_title: Optional[str] = None

class EpisodeResponse(EpisodeBase):
    class Config:
        from_attributes = True

class TranscriptBase(BaseModel):
    transcript_text: str
    episode_id: str

class TranscriptCreate(TranscriptBase):
    pass

class TranscriptUpdate(BaseModel):
    transcript_text: Optional[str] = None
    episode_id: Optional[str] = None

class TranscriptResponse(TranscriptBase):
    transcript_id: int

    class Config:
        from_attributes = True

class AnnotationBase(BaseModel):
    transcript_id: int
    code_id: int

class AnnotationCreate(AnnotationBase):
    pass

class AnnotationUpdate(BaseModel):
    transcript_id: Optional[int] = None
    code_id: Optional[int] = None

class AnnotationResponse(AnnotationBase):
    annotation_id: int

    class Config:
        from_attributes = True

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

# Episode endpoints
@app.post("/episodes/", response_model=EpisodeResponse)
def create_episode(episode: EpisodeCreate, db: Session = Depends(get_db)):
    new_episode = db_manager.create_episode(episode.episode_id, episode.episode_title)
    return new_episode

@app.get("/episodes/", response_model=List[EpisodeResponse])
def read_episodes(db: Session = Depends(get_db)):
    episodes = db_manager.read_all_episodes()
    return episodes

@app.get("/episodes/{episode_id}", response_model=EpisodeResponse)
def read_episode(episode_id: str, db: Session = Depends(get_db)):
    episode = db_manager.read_episode(episode_id)
    if episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode

@app.put("/episodes/{episode_id}", response_model=EpisodeResponse)
def update_episode(episode_id: str, episode: EpisodeUpdate, db: Session = Depends(get_db)):
    db_manager.update_episode(episode_id, episode.episode_title)
    updated_episode = db_manager.read_episode(episode_id)
    if updated_episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    return updated_episode

@app.delete("/episodes/{episode_id}")
def delete_episode(episode_id: str, db: Session = Depends(get_db)):
    db_manager.delete_episode(episode_id)
    return {"message": "Episode deleted successfully"}

# Transcript endpoints
@app.post("/transcripts/", response_model=TranscriptResponse)
def create_transcript(transcript: TranscriptCreate, db: Session = Depends(get_db)):
    new_transcript = db_manager.create_transcript(transcript.transcript_text, transcript.episode_id)
    return new_transcript

@app.get("/transcripts/", response_model=List[TranscriptResponse])
def read_transcripts(db: Session = Depends(get_db)):
    transcripts = db_manager.read_all_transcripts()
    return transcripts

@app.get("/transcripts/{transcript_id}", response_model=TranscriptResponse)
def read_transcript(transcript_id: int, db: Session = Depends(get_db)):
    transcript = db_manager.read_transcript(transcript_id)
    if transcript is None:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript

@app.put("/transcripts/{transcript_id}", response_model=TranscriptResponse)
def update_transcript(transcript_id: int, transcript: TranscriptUpdate, db: Session = Depends(get_db)):
    db_manager.update_transcript(transcript_id, transcript.transcript_text, transcript.episode_id)
    updated_transcript = db_manager.read_transcript(transcript_id)
    if updated_transcript is None:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return updated_transcript

@app.delete("/transcripts/{transcript_id}")
def delete_transcript(transcript_id: int, db: Session = Depends(get_db)):
    db_manager.delete_transcript(transcript_id)
    return {"message": "Transcript deleted successfully"}

# Annotation endpoints
@app.post("/annotations/", response_model=AnnotationResponse)
def create_annotation(annotation: AnnotationCreate, db: Session = Depends(get_db)):
    new_annotation = db_manager.create_annotation(annotation.transcript_id, annotation.code_id)
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
    db_manager.update_annotation(annotation_id, annotation.transcript_id, annotation.code_id)
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

if __name__ == "__main__":
    import uvicorn  # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)