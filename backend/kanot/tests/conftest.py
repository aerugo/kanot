import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..db.crud import DatabaseManager
from ..db.schema import Base
from ..main import create_app, get_db

# Setup test database
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    return DatabaseManager(engine)

@pytest.fixture(scope="module")
def test_app():
    app = create_app(TEST_DB_URL)
    app.dependency_overrides[get_db] = override_get_db
    return app

@pytest.fixture(scope="module")
def test_db():
    # Create the test database and tables
    Base.metadata.create_all(bind=engine)
    
    db_manager = DatabaseManager(engine)
    yield db_manager
    
    # Drop the test database after all tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(test_app):
    # Create a test client using the test app
    return TestClient(test_app)

@pytest.fixture(autouse=True)
def setup_and_teardown(test_db):
    # This fixture will run automatically before and after each test function
    yield
    # After each test, clear all data from tables
    with test_db.get_session() as session:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
