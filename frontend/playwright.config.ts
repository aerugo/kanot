import type { PlaywrightTestConfig } from '@playwright/test';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

const config: PlaywrightTestConfig = {
	webServer: {
		command: 'npm run build && npm run preview',
		port: 4173
	},
	testDir: 'tests',
	testMatch: /(.+\.)?(test|spec)\.[jt]s/,
	globalSetup: async () => {
		// Start the test API
		exec('TEST_MODE=1 uvicorn backend.kanot.main:app --host localhost --port 8888 &');
		
		// Wait for the API to start
		await new Promise(resolve => setTimeout(resolve, 5000));
		
		// Reset the test database
		await execAsync('python ./scripts/populate_test_db.py');
	},
	globalTeardown: async () => {
		// Stop the test API
		await execAsync('pkill -f "uvicorn backend.kanot.main:app"');
	},
	use: {
		baseURL: 'http://localhost:4173',
	},
};

export default config;
