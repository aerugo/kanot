import { expect, test } from '@playwright/test';

// Home page test
test('home page has expected h1', async ({ page }) => {
	await page.goto('/');
	await expect(page.locator('h1')).toBeVisible();
});

// Content page tests
test('Content page loads and displays elements', async ({ page }) => {
	await page.goto('/content');
	await expect(page.locator('h1')).toHaveText('Content');
	await expect(page.locator('table')).toBeVisible();
	await expect(page.locator('tr')).toHaveCount.greaterThan(1);
});

test('Content page search functionality', async ({ page }) => {
	await page.goto('/content');
	await page.fill('input[placeholder="Search element texts..."]', 'test search');
	await page.keyboard.press('Enter');
	await expect(page.locator('tr')).toHaveCount.greaterThan(0);
});

test('Content page filtering', async ({ page }) => {
	await page.goto('/content');
	await page.click('button:has-text("Filter by Series")');
	await page.click('.filter-option >> nth=0');
	await expect(page.locator('.filter-tag')).toBeVisible();
});

test('Content page annotation', async ({ page }) => {
	await page.goto('/content');
	await page.click('button:has-text("+")');
	await page.click('.annotation-dropdown button >> nth=0');
	await expect(page.locator('.code-tag')).toBeVisible();
});

test('Content page batch annotation', async ({ page }) => {
	await page.goto('/content');
	await page.click('input[type="checkbox"] >> nth=0');
	await page.click('input[type="checkbox"] >> nth=1');
	await page.click('button:has-text("Annotate Selected")');
	await page.click('.annotation-dropdown button >> nth=0');
	await page.click('button:has-text("Apply")');
	await expect(page.locator('.code-tag')).toHaveCount(2);
});

// Codes page tests
test('Codes page loads and displays codes', async ({ page }) => {
	await page.goto('/codes');
	await expect(page.locator('h1')).toHaveText('Kanot Code Management');
	await expect(page.locator('table')).toBeVisible();
	await expect(page.locator('tr')).toHaveCount.greaterThan(1);
});

test('Codes page search functionality', async ({ page }) => {
	await page.goto('/codes');
	await page.fill('input[placeholder="Search codes..."]', 'test code');
	await page.keyboard.press('Enter');
	await expect(page.locator('tr')).toHaveCount.greaterThan(0);
});

test('Codes page filtering', async ({ page }) => {
	await page.goto('/codes');
	await page.click('button:has-text("Filter by Type")');
	await page.click('.filter-option >> nth=0');
	await expect(page.locator('.filter-tag')).toBeVisible();
});

test('Add new code', async ({ page }) => {
	await page.goto('/codes');
	await page.click('button:has-text("New Code")');
	await page.fill('input[placeholder="Term"]', 'Test Code');
	await page.fill('input[placeholder="Description"]', 'Test Description');
	await page.selectOption('select', { index: 1 });
	await page.click('button:has-text("Add Code")');
	await expect(page.locator('td:has-text("Test Code")')).toBeVisible();
});

test('Edit existing code', async ({ page }) => {
	await page.goto('/codes');
	await page.click('button:has-text("Edit") >> nth=0');
	await page.fill('input[placeholder="Term"]', 'Updated Code');
	await page.click('button:has-text("Save")');
	await expect(page.locator('td:has-text("Updated Code")')).toBeVisible();
});

test('Delete code', async ({ page }) => {
	await page.goto('/codes');
	const initialCodeCount = await page.locator('tr').count();
	await page.click('button:has-text("Delete") >> nth=0');
	await page.click('button:has-text("Delete")');
	await expect(page.locator('tr')).toHaveCount(initialCodeCount - 1);
});
