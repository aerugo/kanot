import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function globalSetup() {
    try {
        console.log('Resetting the test database...');
        await execAsync('cd ../backend && poetry run python ../scripts/populate_test_db.py');
        console.log('Test database populated');
    } catch (error) {
        console.error('Error in global setup:', error);
        throw error;
    }
}

export default globalSetup;
