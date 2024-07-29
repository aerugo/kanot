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
            console.log('Starting test API server...');
            const command = 'TEST_MODE=1 poetry run uvicorn kanot.main:app --host localhost --port 8888';
            console.log('Executing command:', command);
            
            const { stdout, stderr } = await execAsync(command, { cwd: '../backend' });
            console.log('Test API server start command executed');
            console.log('stdout:', stdout);
            console.log('stderr:', stderr);

            console.log('Checking if the server process is running...');
            const { stdout: psOutput } = await execAsync('ps aux | grep "uvicorn backend.kanot.main:app"');
            console.log('Process check output:', psOutput);

            console.log('Waiting for server to be ready...');
            const serverReady = await waitForServer('http://localhost:8888');
            if (!serverReady) {
                throw new Error('Failed to start the API server');
            }
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
