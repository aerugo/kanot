import type { PlaywrightTestConfig } from '@playwright/test';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

const config: PlaywrightTestConfig = {
	webServer: {
		command: 'npm run build && npm run preview',
		port: 4173
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
