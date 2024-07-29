import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function globalSetup() {
    // Start the test API
    exec('TEST_MODE=1 uvicorn backend.kanot.main:app --host localhost --port 8888 &');
    
    // Wait for the API to start
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Reset the test database
    await execAsync('cd ../backend && poetry run python ../scripts/populate_test_db.py');
}

export default globalSetup;
