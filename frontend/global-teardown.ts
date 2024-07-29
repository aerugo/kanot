import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function globalTeardown() {
    // Stop the test API
    await execAsync('pkill -f "uvicorn backend.kanot.main:app"');
}

export default globalTeardown;
