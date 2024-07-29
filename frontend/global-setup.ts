import { exec } from 'child_process';
import { promisify } from 'util';

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

async function isServerRunning(): Promise<boolean> {
    try {
        const response = await fetch('http://localhost:8888');
        return response.ok;
    } catch (error) {
        return false;
    }
}

async function globalSetup() {
    try {
        console.log('Checking if test API server is already running...');
        const serverRunning = await isServerRunning();

        if (!serverRunning) {
            console.log('Test API server is not running. It will be started by Playwright.');
        } else {
            console.log('Test API server is already running');
        }
        
        console.log('Resetting the test database...');
        await execAsync('cd ../backend && poetry run python ../scripts/populate_test_db.py');
        
        console.log('Test database populated');
    } catch (error) {
        console.error('Error in global setup:', error);
        throw error;
    }
}

export default globalSetup;
