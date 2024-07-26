import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..db.schema import Base
from ..main import app, get_db

# Setup test database
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def test_db():
    # Create the test database and tables
    Base.metadata.create_all(bind=engine)
    
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal()
    
    # Drop the test database after the test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_client():
    # Create a new test client for each test function
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def setup_and_teardown(test_db):
    # This fixture will run automatically before and after each test function
    yield
    # After the test, clear all data from tables
    for table in reversed(Base.metadata.sorted_tables):
        test_db.execute(table.delete())
    test_db.commit()