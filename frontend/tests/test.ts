import { expect, test } from '@playwright/test';
import { fetchPaginatedElements } from '../src/lib/api';

// Home page test
test('home page has expected h1', async ({ page }) => {
	await page.goto('/');
	await expect(page.locator('h1')).toBeVisible();
});

// Content page tests
test('Content page loads and displays elements', async ({ page, request }) => {
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
  
	// Wait for either the table data to load or the "No results found" message to appear
	await Promise.race([
		page.waitForFunction(() => {
			const table = document.querySelector('table');
			return table && table.querySelectorAll('tr').length > 1;
		}, { timeout: 10000 }),
		page.waitForSelector('p.no-results', { state: 'visible', timeout: 10000 })
	]);

	// Additional wait to ensure data is fully loaded
	await page.waitForTimeout(1000);

	// Check if there are any rows in the table or if the "No results found" message is displayed
	const hasTable = await page.locator('table').isVisible();
	const noResultsMessage = await page.locator('p.no-results').isVisible();

	if (hasTable) {
		// If the table is visible, check if it has content
		await expect(page.locator('table')).toBeVisible();
		const rowCount = await page.locator('tr').count();
		console.log(`Number of rows found: ${rowCount}`);
		expect(rowCount).toBeGreaterThan(0); // Expect at least the header row
		if (rowCount === 1) {
			console.log('Only header row is present, checking for "No results found" message');
			const noResultsMessage = await page.locator('p.no-results').textContent();
			console.log(`No results message: ${noResultsMessage}`);
			expect(noResultsMessage).toBe('No results found.');
		} else if (rowCount > 1) {
			// Fetch elements from the API
			const apiElements = await fetchPaginatedElements(1, 100);
			
			// Get the first element from the table
			const firstTableElement = await page.locator('table tbody tr:first-child').textContent();
			
			// Compare the first element from the API with the first element in the table
			expect(firstTableElement).toContain(apiElements[0].element_text);
		} else {
			throw new Error('Unexpected table state: no rows found');
		}
	} else if (noResultsMessage) {
		// If the "No results found" message is displayed
		await expect(page.locator('p.no-results')).toBeVisible();
		const message = await page.locator('p.no-results').textContent();
		console.log(`No results message: ${message}`);
		expect(message).toBe('No results found.');
	} else {
		throw new Error('Neither table nor "No results found" message was displayed');
	}
});
