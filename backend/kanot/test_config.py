import os

# Local database configuration
LOCAL_DB_URL = "sqlite:///./local_database.db"

# Test database configuration
TEST_DB_URL = "sqlite:///./test_database.db"

# Test API configuration
TEST_API_HOST = "localhost"
TEST_API_PORT = 8888

# Path to the script for populating the test database
POPULATE_TEST_DB_SCRIPT = "./scripts/populate_test_db.py"

# Ensure the test database directory exists
os.makedirs(os.path.dirname(TEST_DB_URL.replace("sqlite:///", "")), exist_ok=True)
import os

# Local database configuration
LOCAL_DB_URL = "sqlite:///./local_database.db"

# Test database configuration
TEST_DB_URL = "sqlite:///./test_database.db"

# Test API configuration
TEST_API_HOST = "localhost"
TEST_API_PORT = 8888

# Path to the script for populating the test database
POPULATE_TEST_DB_SCRIPT = "./scripts/populate_test_db.py"

# Ensure the test database directory exists
os.makedirs(os.path.dirname(TEST_DB_URL.replace("sqlite:///", "")), exist_ok=True)
