import pandas as pd
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.test_config import TEST_DB_URL

def preprocess_glossary_data() -> dict[str, pd.DataFrame]:
    # Your existing implementation
    pass

def setup_database(sqlite_uri) -> Session:
    # Your existing implementation
    pass

def insert_data(df: pd.DataFrame, model: DeclarativeMeta, session: Session) -> None:
    # Your existing implementation
    pass

def load_data(sqliteuri: str):
    # Your existing implementation
    pass

if __name__ == '__main__':
    load_data(TEST_DB_URL.replace("sqlite:///", ""))
