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
  
	// Count the number of rows and check if it's at least 1 (the header row)
	const rowCount = await page.locator('tr').count();
	console.log(`Number of rows found: ${rowCount}`);
	expect(rowCount).toBeGreaterThanOrEqual(1);
  
	// Check if there's a message indicating no results
	const noResultsMessage = await page.locator('p.no-results').textContent();
	console.log(`No results message: ${noResultsMessage}`);
  
	// If there's only one row (the header), check for the no results message
	if (rowCount === 1) {
	  expect(noResultsMessage).toBe('No results found.');
	}
  });
