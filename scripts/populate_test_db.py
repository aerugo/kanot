import pandas as pd


def preprocess_glossary_data() -> dict[str, pd.DataFrame]:

    # Load the CSV files into DataFrames and preprocess them

    # Load the CSV files into DataFrames
    codes_df = pd.read_csv('./_temp/glossary.csv')  # type: ignore
    elements_df = pd.read_csv('./_temp/transcripts.csv')  # type: ignore

    # Rename columns according to the provided mapping
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
    # drop the columns that are not element_id, element_text, segment_id, segment_title, code_ids
    elements_df = elements_df[['element_id', 'element_text', 'segment_id', 'segment_title', 'code_ids']]

    elements_df['code_ids'] = elements_df['code_ids'].fillna('') # type: ignore

    # remove any rows in the elements_df where the element_text is empty
    elements_df = elements_df[elements_df['element_text'].notnull()]

    # create a dataframe with all unique segment_id and segment_title
    segment_df = elements_df[['segment_id', 'segment_title']].drop_duplicates()

    # create a dataframe series_df with autoincrementing column series_id and series_title and add one row with series_title = 'Conflicted Podcast'
    series_df = pd.DataFrame({'series_id': [1], 'series_title': ['Conflicted Podcast']})

    # add a column series_id to the segment_df dataframe and set the value to 1 for all rows
    segment_df['series_id'] = 1

    # create a dataframe with all unique glossary type
    code_type_df = codes_df[['type']].drop_duplicates()
    # rename the column to type_name
    code_type_df = code_type_df.rename(columns={'type': 'type_name'})
    # create an incrementing type_id column
    code_type_df['type_id'] = range(1, len(code_type_df) + 1)

    # Create a column type_id in the codes_df dataframe and map the type_name to the type_id
    # Merge the code_type_df with the codes_df on type = type_name
    codes_df = codes_df.merge(code_type_df, left_on='type', right_on='type_name', how='left') # type: ignore
    codes_df = codes_df.rename(columns={'type_name': 'type_id'})
    codes_df = codes_df[['code_id', 'term', 'description', 'type_id', 'reference', 'coordinates']]

    # create a dataframe project_df with autoincrementing column project_id and project_title and projcet_description and add one row with project_title = 'Conflicted Glossary' and project_description = 'Glossary for the Conflicted Podcast'
    project_df = pd.DataFrame({'project_id': [1], 'project_title': ['Conflicted Glossary'], 'project_description': ['Glossary for the Conflicted Podcast']})

    # Add a column project_id to the codes_df dataframe and set the value to 1 for all rows
    codes_df['project_id'] = 1

    # Add a column project_id to the code_type_df dataframe and set the value to 1 for all rows
    code_type_df['project_id'] = 1

    # Add a column project_id to the elements_df dataframe and set the value to 1 for all rows
    elements_df['project_id'] = 1

    # Add a column project_id to the segment_df dataframe and set the value to 1 for all rows
    segment_df['project_id'] = 1

    # Add a column project_id to the series_df dataframe and set the value to 1 for all rows
    series_df['project_id'] = 1

    # Create a new DataFrame annotations_df with columns element_id, code_id
    annotations_df = pd.DataFrame(columns=['element_id', 'code_id'])

    # Iterate over each row in elements_df and add rows to annotations_df
    rows_to_add = []
    for index, row in elements_df.iterrows():
        element_id = row['element_id']
        code_ids = row['code_ids'].split(';')
        for code_id in code_ids if code_ids != [''] else []:
            code_id = int(code_id)
            rows_to_add.append({'element_id': element_id, 'code_id': code_id})

    elements_df.drop(columns=['code_ids', 'segment_title'], inplace=True) # type: ignore

    # Convert list of rows to DataFrame and concatenate
    annotations_df = pd.concat([annotations_df, pd.DataFrame(rows_to_add)], ignore_index=True)

    # Convert code_id to int
    annotations_df['code_id'] = annotations_df['code_id'].astype(int)

    # Add a column annotation_id to annotations_df
    annotations_df['annotation_id'] = annotations_df.index

    # Add a column project_id to the annotations_df dataframe and set the value to 1 for all rows
    annotations_df['project_id'] = 1

    return {
        'project_df': project_df,
        'code_type_df': code_type_df,
        'codes_df': codes_df,
        'series_df': series_df,
        'segment_df': segment_df,
        'elements_df': elements_df,
        'annotations_df': annotations_df
    }

# Define database connection

from typing import Any, Hashable

from kanot.db.schema import (
    Annotation,
    Code,
    CodeType,
    Element,
    Project,
    Segment,
    Series,
    create_database,
    drop_database,
)
from sqlalchemy import Engine, create_engine, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session, sessionmaker


def setup_database(sqlite_uri) -> Session:
    # Create a connection to the SQLite database
    engine: Engine = create_engine(sqlite_uri, echo=True)
    MySession = sessionmaker(bind=engine)
    session = MySession()

    drop = True
    if drop:
        # Drop all the tables in the database
        drop_database(engine)

    # Create the tables in the database
    create_database(engine)

    return session


from typing import Any, Hashable

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session


# Insert data from a DataFrame
def insert_data(df: pd.DataFrame, model: DeclarativeMeta, session: Session) -> None:
    data: list[dict[Hashable, Any]] = df.to_dict(orient='records') # type: ignore
    
    try:
        session.bulk_insert_mappings(model, data) # type: ignore
        session.commit()
    except IntegrityError as e:
        print(f"Unique constraint violation: {e}")
        session.rollback()


def load_data(sqliteuri: str):
    # Preprocess the glossary data
    data = preprocess_glossary_data()

    # Extract the DataFrames
    project_df = data['project_df']
    code_type_df = data['code_type_df']
    codes_df = data['codes_df']
    series_df = data['series_df']
    segment_df = data['segment_df']
    elements_df = data['elements_df']
    annotations_df = data['annotations_df']

    # Setup the database
    session = setup_database(sqliteuri)

    # Insert data into the projects table
    insert_data(project_df, Project, session)

    # Insert data into the code_types table
    insert_data(code_type_df, CodeType, session)

    # Insert data into the codes table
    insert_data(codes_df, Code, session)

    # Insert data into the series table
    insert_data(series_df, Series, session)

    # Insert data into the segments table
    insert_data(segment_df, Segment, session)

    # Insert data into the elements table
    insert_data(elements_df, Element, session)

    # Insert data into the annotations table
    insert_data(annotations_df, Annotation, session)

    # Close the session
    session.close()

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        load_data(sys.argv[1])

    else:
        load_data('sqlite:///../backend/test_database.db')