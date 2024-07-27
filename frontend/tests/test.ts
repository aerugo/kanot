import { expect, test } from '@playwright/test';

// Home page test
test('home page has expected h1', async ({ page }) => {
	await page.goto('/');
	await expect(page.locator('h1')).toBeVisible();
});

// Content page tests
test('Content page loads and displays elements', async ({ page }) => {
	// Navigate to the content page
	await page.goto('/content');
  
	// Wait for an element that indicates the page has loaded
	await page.waitForSelector('h1:has-text("Content")', { timeout: 10000 });
  
	// Check if the h1 is visible and has the correct text
	await expect(page.locator('h1')).toBeVisible();
	await expect(page.locator('h1')).toHaveText('Content');
  
	// Wait for the table to be visible
	await page.waitForSelector('table', { state: 'visible', timeout: 10000 });
  
	// Check if the table is visible
	await expect(page.locator('table')).toBeVisible();
  
	// Wait for at least one row to appear
	await page.waitForSelector('tr', { state: 'visible', timeout: 10000 });
  
	// Count the number of rows and check if it's greater than 1 (assuming there's a header row)
	const rowCount = await page.locator('tr').count();
	expect(rowCount).toBeGreaterThan(1);
  
	// Log some information for debugging
	console.log(`Number of rows found: ${rowCount}`);
  });