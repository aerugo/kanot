import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function globalTeardown() {
    try {
        // Stop the test API
        await execAsync('pkill -f "uvicorn backend.kanot.main:app"');
    } catch (error) {
        console.log('No uvicorn process found to kill. This is not necessarily an error.');
    }
}

export default globalTeardown;
