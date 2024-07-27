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
  
	// Check if there are any rows in the table or if the "No results found" message is displayed
	const hasRows = await page.locator('tr').count() > 1;
	const noResultsMessage = await page.locator('p.no-results').isVisible();

	if (hasRows) {
		// If there are rows, check if the table is visible and has content
		await expect(page.locator('table')).toBeVisible();
		const rowCount = await page.locator('tr').count();
		console.log(`Number of rows found: ${rowCount}`);
		expect(rowCount).toBeGreaterThan(1);
	} else {
		// If there are no rows, check if the "No results found" message is displayed
		await expect(page.locator('p.no-results')).toBeVisible();
		const message = await page.locator('p.no-results').textContent();
		console.log(`No results message: ${message}`);
		expect(message).toBe('No results found.');
	}
  });
