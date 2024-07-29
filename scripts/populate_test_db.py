import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.kanot.db.schema import (
    Annotation,
    Code,
    CodeType,
    Element,
    Project,
    Segment,
    Series,
    create_database,
)


def populate_test_db():
    # Create a connection to the SQLite database
    db_path = project_root / 'backend' / 'test_database.db'
    engine = create_engine(f'sqlite:///{db_path}', echo=True)
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
    codes_df = codes_df[['code_id', 'term', 'description', 'type_name', 'reference', 'coordinates']]

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

    # Insert data into tables
    project_df.to_sql('projects', engine, if_exists='replace', index=False)
    code_type_df.to_sql('code_types', engine, if_exists='replace', index=False)
    codes_df['project_id'] = 1  # Add project_id column
    codes_df.to_sql('codes', engine, if_exists='replace', index=False)
    series_df.to_sql('series', engine, if_exists='replace', index=False)
    segment_df.to_sql('segments', engine, if_exists='replace', index=False)
    elements_df.to_sql('elements', engine, if_exists='replace', index=False)
    annotations_df.to_sql('annotations', engine, if_exists='replace', index=False)

    session.close()

if __name__ == "__main__":
    populate_test_db()
