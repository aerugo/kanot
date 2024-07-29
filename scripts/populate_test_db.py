import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from backend.kanot.db.schema import create_database, drop_database, Project, CodeType, Code, Series, Segment, Element, Annotation


def populate_test_db():
    # Create a connection to the SQLite database
    db_path = project_root / 'backend' / 'local_database.db'
    engine = create_engine(f'sqlite:///{db_path}', echo=True)
    
    # Drop existing database and create a new one
    drop_database(engine)
    create_database(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    # Load CSV files
    codes_df = pd.read_csv('backend/_temp/glossary.csv')
    elements_df = pd.read_csv('backend/_temp/transcripts.csv')

    # Rename columns
    codes_df = codes_df.rename(columns={
        'Glossary ID': 'code_id',
        'Term': 'term',
        'Description': 'description',
        'Type': 'type',
        'Read more': 'reference',
        'Lat/Long': 'coordinates'
    })

    elements_df = elements_df.rename(columns={
        'Text ID': 'element_id',
        'Text': 'element_text',
        'Episode ID': 'segment_id',
        'Episode': 'segment_title',
        'Glossary IDs': 'code_ids'
    })
    elements_df = elements_df[['element_id', 'element_text', 'segment_id', 'segment_title', 'code_ids']]
    elements_df['code_ids'] = elements_df['code_ids'].fillna('')
    elements_df = elements_df[elements_df['element_text'].notnull()]

    segment_df = elements_df[['segment_id', 'segment_title']].drop_duplicates()
    series_df = pd.DataFrame({'series_id': [1], 'series_title': ['Conflicted Podcast']})
    segment_df['series_id'] = 1

    code_type_df = codes_df[['type']].drop_duplicates()
    code_type_df = code_type_df.rename(columns={'type': 'type_name'})
    code_type_df['type_id'] = range(1, len(code_type_df) + 1)

    codes_df = codes_df.merge(code_type_df, left_on='type', right_on='type_name', how='left')
    codes_df = codes_df.rename(columns={'type': 'type_name'})
    codes_df = codes_df.merge(code_type_df[['type_name', 'type_id']], on='type_name', how='left')
    codes_df = codes_df[['code_id', 'term', 'description', 'type_id', 'reference', 'coordinates']]

    project_df = pd.DataFrame({'project_id': [1], 'project_title': ['Conflicted Glossary'], 'project_description': ['Glossary for the Conflicted Podcast']})

    codes_df['project_id'] = 1
    code_type_df['project_id'] = 1
    elements_df['project_id'] = 1
    segment_df['project_id'] = 1
    series_df['project_id'] = 1

    # Create annotations DataFrame
    annotations_df = pd.DataFrame(columns=['element_id', 'code_id'])
    rows_to_add = []
    for index, row in elements_df.iterrows():
        element_id = row['element_id']
        code_ids = row['code_ids'].split(';')
        for code_id in code_ids if code_ids != [''] else []:
            code_id = int(code_id)
            rows_to_add.append({'element_id': element_id, 'code_id': code_id})

    elements_df.drop(columns=['code_ids', 'segment_title'], inplace=True)
    annotations_df = pd.concat([annotations_df, pd.DataFrame(rows_to_add)], ignore_index=True)
    annotations_df['code_id'] = annotations_df['code_id'].astype(int)
    annotations_df['annotation_id'] = annotations_df.index
    annotations_df['project_id'] = 1

    # Define a function to insert data from a DataFrame
    def insert_data(df, model, session):
        data = df.to_dict(orient='records')
        for record in data:
            try:
                instance = model(**record)
                session.add(instance)
                session.commit()
            except IntegrityError as e:
                print(f"Unique constraint violation: {e}")
                session.rollback()
            except Exception as e:
                print(f"Error inserting record: {e}")
                session.rollback()

    # Insert data into tables
    insert_data(project_df, Project, session)
    insert_data(code_type_df, CodeType, session)
    insert_data(codes_df, Code, session)
    insert_data(series_df, Series, session)
    insert_data(segment_df, Segment, session)
    insert_data(elements_df, Element, session)
    insert_data(annotations_df, Annotation, session)

    # Debug: Print the number of records in each table
    print(f"Number of projects: {session.query(Project).count()}")
    print(f"Number of code types: {session.query(CodeType).count()}")
    print(f"Number of codes: {session.query(Code).count()}")
    print(f"Number of series: {session.query(Series).count()}")
    print(f"Number of segments: {session.query(Segment).count()}")
    print(f"Number of elements: {session.query(Element).count()}")
    print(f"Number of annotations: {session.query(Annotation).count()}")

    session.close()

if __name__ == "__main__":
    print("Starting database population...")
    populate_test_db()
    print("Database population completed.")
