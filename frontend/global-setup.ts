import { exec } from 'child_process';
import { promisify } from 'util';
import fetch from 'node-fetch';

const execAsync = promisify(exec);

async function waitForServer(url: string, maxRetries = 10, delay = 1000): Promise<boolean> {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url);
            if (response.ok) {
                console.log('Server is ready');
                return true;
            }
        } catch (error) {
            console.log(`Attempt ${i + 1}: Server not ready yet...`);
        }
        await new Promise(resolve => setTimeout(resolve, delay));
    }
    console.error('Server failed to start after maximum retries');
    return false;
}

async function globalSetup() {
    try {
        // Start the test API
        await execAsync('TEST_MODE=1 uvicorn backend.kanot.main:app --host localhost --port 8888 &');
        
        console.log('Test API server started');

        // Wait for the API to be ready
        const serverReady = await waitForServer('http://localhost:8888');
        if (!serverReady) {
            throw new Error('Failed to start the API server');
        }
        
        // Reset the test database
        await execAsync('cd ../backend && poetry run python ../scripts/populate_test_db.py');
        
        console.log('Test database populated');
    } catch (error) {
        console.error('Error in global setup:', error);
        throw error;
    }
}

export default globalSetup;
