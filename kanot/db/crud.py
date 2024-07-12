from typing import Any, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from .schema import Annotation, Code, CodeType, Episode, Transcript, create_database


class DatabaseManager:
    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.Session = sessionmaker(bind=engine)
        create_database(engine)
    
    def create_code_type(self, type_name: str) -> None:
        session = self.Session()
        new_code_type = CodeType(type_name=type_name)
        try:
            session.add(new_code_type)
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"CodeType with type_name={type_name} already exists.")
        finally:
            session.close()
    
    def read_code_type(self, type_id: int) -> Optional[CodeType]:
        session = self.Session()
        code_type: Optional[CodeType] = session.query(CodeType).filter_by(type_id=type_id).first()
        session.close()
        return code_type
    
    def update_code_type(self, type_id: int, type_name: str) -> None:
        session = self.Session()
        code_type: Optional[CodeType] = session.query(CodeType).filter_by(type_id=type_id).first()
        if code_type:
            try:
                code_type.type_name = type_name
                session.commit()
            except IntegrityError:
                session.rollback()
                print(f"Failed to update CodeType to type_name={type_name} due to a unique constraint violation.")
        session.close()
    
    def delete_code_type(self, type_id: int) -> None:
        session = self.Session()
        code_type: Optional[CodeType] = session.query(CodeType).filter_by(type_id=type_id).first()
        if code_type:
            session.delete(code_type)
            session.commit()
        session.close()
    
    def create_code(self, term: str, description: str, type_id: int, reference: str, coordinates: str) -> None:
        session = self.Session()
        new_code = Code(term=term, description=description, type_id=type_id, reference=reference, coordinates=coordinates)
        try:
            session.add(new_code)
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"Code with term={term} already exists.")
        finally:
            session.close()
    
    def read_code(self, code_id: int) -> Optional[Code]:
        session = self.Session()
        code: Optional[Code] = session.query(Code).filter_by(code_id=code_id).first()
        session.close()
        return code
    
    def update_code(self, code_id: int, term: Optional[str] = None, description: Optional[str] = None, type_id: Optional[int] = None, reference: Optional[str] = None, coordinates: Optional[str] = None) -> None:
        session = self.Session()
        code: Optional[Code] = session.query(Code).filter_by(code_id=code_id).first()
        if code:
            try:
                if term:
                    code.term = term
                if description:
                    code.description = description
                if type_id:
                    code.type_id = type_id
                if reference:
                    code.reference = reference
                if coordinates:
                    code.coordinates = coordinates
                session.commit()
            except IntegrityError:
                session.rollback()
                print("Failed to update Code due to a unique constraint violation.")
        session.close()
    
    def delete_code(self, code_id: int) -> None:
        session = self.Session()
        code: Optional[Code] = session.query(Code).filter_by(code_id=code_id).first()
        if code:
            session.delete(code)
            session.commit()
        session.close()

    def create_episode(self, episode_id: str, episode_title: str) -> None:
        session = self.Session()
        new_episode = Episode(episode_id=episode_id, episode_title=episode_title)
        try:
            session.add(new_episode)
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"Episode with episode_id={episode_id} or episode_title={episode_title} already exists.")
        finally:
            session.close()
    
    def read_episode(self, episode_id: str) -> Optional[Episode]:
        session = self.Session()
        episode: Optional[Episode] = session.query(Episode).filter_by(episode_id=episode_id).first()
        session.close()
        return episode
    
    def update_episode(self, episode_id: str, episode_title: Optional[str] = None) -> None:
        session = self.Session()
        episode: Optional[Episode] = session.query(Episode).filter_by(episode_id=episode_id).first()
        if episode:
            try:
                if episode_title:
                    episode.episode_title = episode_title
                session.commit()
            except IntegrityError:
                session.rollback()
                print("Failed to update Episode due to a unique constraint violation.")
        session.close()
    
    def delete_episode(self, episode_id: str) -> None:
        session = self.Session()
        episode: Optional[Episode] = session.query(Episode).filter_by(episode_id=episode_id).first()
        if episode:
            session.delete(episode)
            session.commit()
        session.close()
    
    def create_transcript(self, transcript_text: str, episode_id: str) -> None:
        session = self.Session()
        new_transcript = Transcript(transcript_text=transcript_text, episode_id=episode_id)
        try:
            session.add(new_transcript)
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"Transcript for episode_id={episode_id} already exists.")
        finally:
            session.close()
    
    def read_transcript(self, transcript_id: int) -> Optional[Transcript]:
        session = self.Session()
        transcript: Optional[Transcript] = session.query(Transcript).filter_by(transcript_id=transcript_id).first()
        session.close()
        return transcript
    
    def update_transcript(self, transcript_id: int, transcript_text: Optional[str] = None, episode_id: Optional[str] = None) -> None:
        session = self.Session()
        transcript: Optional[Transcript] = session.query(Transcript).filter_by(transcript_id=transcript_id).first()
        if transcript:
            try:
                if transcript_text:
                    transcript.transcript_text = transcript_text
                if episode_id:
                    transcript.episode_id = episode_id
                session.commit()
            except IntegrityError:
                session.rollback()
                print("Failed to update Transcript due to a unique constraint violation.")
        session.close()
    
    def delete_transcript(self, transcript_id: int) -> None:
        session = self.Session()
        transcript: Optional[Transcript] = session.query(Transcript).filter_by(transcript_id=transcript_id).first()
        if transcript:
            session.delete(transcript)
            session.commit()
        session.close()
    
    def create_annotation(self, transcript_id: int, code_id: int) -> None:
        session = self.Session()
        new_annotation = Annotation(transcript_id=transcript_id, code_id=code_id)
        try:
            session.add(new_annotation)
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"Annotation with transcript_id={transcript_id} and code_id={code_id} already exists.")
        finally:
            session.close()
    
    def read_annotation(self, annotation_id: int) -> Optional[Annotation]:
        session = self.Session()
        annotation: Optional[Annotation] = session.query(Annotation).filter_by(annotation_id=annotation_id).first()
        session.close()
        return annotation
    
    def update_annotation(self, annotation_id: int, transcript_id: Optional[int] = None, code_id: Optional[int] = None) -> None:
        session = self.Session()
        annotation: Optional[Annotation] = session.query(Annotation).filter_by(annotation_id=annotation_id).first()
        if annotation:
            try:
                if transcript_id:
                    annotation.transcript_id = transcript_id
                if code_id:
                    annotation.code_id = code_id
                session.commit()
            except IntegrityError:
                session.rollback()
                print("Failed to update Annotation due to a unique constraint violation.")
        session.close()
    
    def delete_annotation(self, annotation_id: int) -> None:
        session = self.Session()
        annotation: Optional[Annotation] = session.query(Annotation).filter_by(annotation_id=annotation_id).first()
        if annotation:
            session.delete(annotation)
            session.commit()
        session.close()