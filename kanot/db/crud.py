from typing import Any, Optional

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from .schema import Annotation, Code, CodeType, Episode, Transcript, create_database


class DatabaseManager:
    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.Session = sessionmaker(bind=engine)
        create_database(engine)

    # CodeType CRUD
    
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
    
    def read_all_code_types(self) -> list[CodeType]:
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
                print(f"Failed to update CodeType to type_name={type_name} due to a unique constraint violation.")
        session.close()
    
    def delete_code_type(self, type_id: int) -> None:
        session = self.Session()
        code_type: Optional[CodeType] = session.query(CodeType).filter_by(type_id=type_id).first()
        if code_type:
            session.delete(code_type)
            session.commit()
        session.close()

    # Code CRUD
    
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
    
    def read_all_codes(self) -> list[Code]:
        session = self.Session()
        codes = session.query(Code).all()
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
                print("Failed to update Code due to a unique constraint violation.")
        session.close()
    
    def delete_code(self, code_id: int) -> None:
        session = self.Session()
        code: Optional[Code] = session.query(Code).filter_by(code_id=code_id).first()
        if code:
            session.delete(code)
            session.commit()
        session.close()

    # Episode CRUD

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
    
    def read_all_episodes(self) -> list[Episode]:
        session = self.Session()
        episodes = session.query(Episode).all()
        session.close()
        return episodes
    
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

    # Transcript CRUD
    
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
    
    def read_all_transcripts(self) -> list[Transcript]:
        session = self.Session()
        transcripts = session.query(Transcript).all()
        session.close()
        return transcripts
    
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

    # Annotation CRUD
    
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
    
    def read_all_annotations(self) -> list[Annotation]:
        session = self.Session()
        annotations = session.query(Annotation).all()
        session.close()
        return annotations
    
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

    def merge_codes(self, code_a_id: int, code_b_id: int) -> None:
        session = self.Session()
        try:
            # Get both codes
            code_a = session.query(Code).filter_by(code_id=code_a_id).first()
            code_b = session.query(Code).filter_by(code_id=code_b_id).first()

            if not code_a or not code_b:
                print(f"One or both codes (ID: {code_a_id}, {code_b_id}) do not exist.")
                return

            # Get all annotations for code_a
            annotations_a = session.query(Annotation).filter_by(code_id=code_a_id).all()

            for annotation in annotations_a:
                # Check if there's already an annotation for this transcript with code_b
                existing_annotation = session.query(Annotation).filter(
                    and_(Annotation.transcript_id == annotation.transcript_id,
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
            print(f"Successfully merged Code {code_a_id} into Code {code_b_id}")
        except Exception as e:
            session.rollback()
            print(f"Failed to merge codes: {str(e)}")
        finally:
            session.close()

    def get_annotations_for_code(self, code_id: int) -> list[Annotation]:
        session = self.Session()
        try:
            annotations = session.query(Annotation).filter_by(code_id=code_id).all()
            return annotations
        finally:
            session.close()