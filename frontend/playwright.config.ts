import type { PlaywrightTestConfig } from '@playwright/test';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const config: PlaywrightTestConfig = {
	webServer: {
		command: 'npm run build && npm run preview',
		port: 4173,
		env: {
			TEST_MODE: '1',
			VITE_TEST_MODE: '1',
			VITE_API_URL: 'http://localhost:8888'
		}
	},
	testDir: 'tests',
	testMatch: /(.+\.)?(test|spec)\.[jt]s/,
	globalSetup: path.join(__dirname, 'global-setup.ts'),
	globalTeardown: path.join(__dirname, 'global-teardown.ts'),
	use: {
		baseURL: 'http://localhost:4173',
	},
};

export default config;
