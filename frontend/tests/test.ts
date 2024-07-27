import { expect, test } from '@playwright/test';

// Test for the home page
test('home page has expected title and navigation', async ({ page }) => {
  await page.goto('/');
  
  // Check the page title
  await expect(page).toHaveTitle('Welcome to Kanot Code Management');
  
  // Check for the main heading
  const heading = page.locator('h1');
  await expect(heading).toBeVisible();
  await expect(heading).toHaveText('Welcome to Kanot Code Management');
  
  // Check for navigation links
  await expect(page.locator('nav a[href="/codes"]')).toBeVisible();
  await expect(page.locator('nav a[href="/content"]')).toBeVisible();
});

// Test for the Codes page
test('codes page displays codes list', async ({ page }) => {
  await page.goto('/codes');
  
  // Check the page heading
  const heading = page.locator('h1');
  await expect(heading).toBeVisible();
  await expect(heading).toHaveText('Kanot Code Management');
  
  // Check for the presence of the codes list
  await expect(page.locator('.codes-list')).toBeVisible();
  
  // Check for the presence of the "New Code" button
  await expect(page.locator('button:has-text("New Code")')).toBeVisible();
});

// Test for the Content page
test('content page displays content list', async ({ page }) => {
  await page.goto('/content');
  
  // Check the page heading
  const heading = page.locator('h1');
  await expect(heading).toBeVisible();
  await expect(heading).toHaveText('Content');
  
  // Check for the presence of the search bar
  await expect(page.locator('input[placeholder="Search element texts..."]')).toBeVisible();
  
  // Check for the presence of the table
  await expect(page.locator('table')).toBeVisible();
});

// Test the search functionality on the Content page
test('content search updates results', async ({ page }) => {
  await page.goto('/content');
  
  // Type a search term
  await page.fill('input[placeholder="Search element texts..."]', 'test search');
  
  // Wait for the search results to update
  await page.waitForTimeout(1000); // Wait for debounce
  
  // Check if the table is still visible (assuming it always shows, even with no results)
  await expect(page.locator('table')).toBeVisible();
});

// Test adding a new code
test('can open new code form', async ({ page }) => {
  await page.goto('/codes');
  
  // Click the "New Code" button
  await page.click('button:has-text("New Code")');
  
  // Check if the form is visible
  await expect(page.locator('form')).toBeVisible();
  
  // Check for form fields
  await expect(page.locator('input[placeholder="Term"]')).toBeVisible();
  await expect(page.locator('input[placeholder="Description"]')).toBeVisible();
  await expect(page.locator('select')).toBeVisible();
});

// Test for filtering codes by type
test('can filter codes by type', async ({ page }) => {
  await page.goto('/codes');
  
  // Wait for the codes list to be visible
  await page.waitForSelector('.codes-list', { state: 'visible' });
  
  // Get the initial number of visible codes
  const initialCodeCount = await page.locator('.codes-list tr').count();
  
  // Open the filter dropdown
  await page.click('button:has-text("Filter by Type")');
  
  // Wait for the dropdown to be visible
  await page.waitForSelector('.filter-option', { state: 'visible' });
  
  // Select the first filter option
  await page.click('.filter-option:first-child');
  
  // Wait for the filter to be applied (increased timeout)
  await page.waitForTimeout(10000);
  
  // Log the current state of the page
  console.log('Page content after filtering:', await page.content());
  
  // Check if the filter tag is visible with a longer timeout
  const filterTag = page.locator('.filter-tag');
  console.log('Filter tag exists:', await filterTag.count() > 0);
  if (await filterTag.count() > 0) {
    console.log('Filter tag HTML:', await filterTag.evaluate(el => el.outerHTML));
  } else {
    console.log('Filter tag not found. Checking for other elements:');
    console.log('Filter dropdown visible:', await page.locator('.filter-dropdown').isVisible());
    console.log('Selected filters container:', await page.locator('.selected-filters').innerHTML());
  }
  
  // Get the new number of visible codes
  const filteredCodeCount = await page.locator('.codes-list tr').count();
  
  // Log the counts for debugging
  console.log('Initial code count:', initialCodeCount);
  console.log('Filtered code count:', filteredCodeCount);
  
  // Check if the number of visible codes has changed
  expect(filteredCodeCount).not.toBe(initialCodeCount);
  
  // Only check for the filter tag visibility if the code count has changed
  if (filteredCodeCount !== initialCodeCount) {
    await expect(filterTag).toBeVisible({ timeout: 30000 });
  } else {
    console.log('Code count did not change. Filter may not have been applied successfully.');
  }
  
  // Ensure that the codes list is still visible
  await expect(page.locator('.codes-list')).toBeVisible();
});
  
  // Test for editing a code
  test('can edit an existing code', async ({ page }) => {
	await page.goto('/codes');
	
	// Click the edit button on the first code (adjust selector as needed)
	await page.click('.codes-list tr:first-child button:has-text("Edit")');
	
	// Check if the edit modal is visible
	await expect(page.locator('.modal')).toBeVisible();
	
	// Fill in a new term
	await page.fill('input[placeholder="Term"]', 'Updated Code Term');
	
	// Save the changes
	await page.click('button:has-text("Save")');
	
	// Check if the modal closes
	await expect(page.locator('.modal')).not.toBeVisible();
	
	// Check if the updated term is visible in the list (this might need adjustment)
	await expect(page.locator('.codes-list')).toContainText('Updated Code Term');
  });
  
  // Test for deleting a code
  test('can delete a code', async ({ page }) => {
	await page.goto('/codes');
	
	// Store the initial number of codes
	const initialCodeCount = await page.locator('.codes-list tr').count();
	
	// Click the delete button on the first code
	await page.click('.codes-list tr:first-child button:has-text("Delete")');
	
	// Confirm deletion in the modal
	await page.click('.modal button:has-text("Delete")');
	
	// Wait for the deletion to be reflected in the UI
	await page.waitForFunction(
	  (expectedCount) => document.querySelectorAll('.codes-list tr').length === expectedCount,
	  initialCodeCount - 1,
	  { timeout: 5000 }
	);
	
	// Check if the number of codes has decreased
	const newCodeCount = await page.locator('.codes-list tr').count();
	expect(newCodeCount).toBe(initialCodeCount - 1);
  });
  
  // Test for pagination on the Content page
  test('content pagination loads more items', async ({ page }) => {
	await page.goto('/content');
	
	// Get the initial number of rows
	const initialRowCount = await page.locator('table tbody tr').count();
	
	// Scroll to the bottom of the page to trigger loading more items
	await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
	
	// Wait for new items to load (adjust timeout as needed)
	await page.waitForTimeout(1000);
	
	// Check if the number of rows has increased
	const newRowCount = await page.locator('table tbody tr').count();
	expect(newRowCount).toBeGreaterThan(initialRowCount);
  });
  
  // Test for adding an annotation to an element
  test('can add annotation to an element', async ({ page }) => {
	await page.goto('/content');
	
	// Click the add annotation button on the first element
	await page.click('table tbody tr:first-child button.add-code');
	
	// Check if the annotation dropdown is visible
	await expect(page.locator('.annotation-dropdown')).toBeVisible();
	
	// Select the first code from the dropdown
	await page.click('.annotation-dropdown .filter-option:first-child');
	
	// Check if a new code tag is added to the element
	await expect(page.locator('table tbody tr:first-child .code-tag')).toBeVisible();
  });
  
  // Test for removing an annotation from an element
  test('can remove annotation from an element', async ({ page }) => {
	await page.goto('/content');
	
	// Ensure there's at least one annotation
	await page.click('table tbody tr:first-child button.add-code');
	await page.click('.annotation-dropdown .filter-option:first-child');
	
	// Get the initial number of annotations
	const initialAnnotationCount = await page.locator('table tbody tr:first-child .code-tag').count();
	
	// Remove the first annotation
	await page.click('table tbody tr:first-child .code-tag button');
	
	// Check if the number of annotations has decreased
	await expect(page.locator('table tbody tr:first-child .code-tag')).toHaveCount(initialAnnotationCount - 1);
  });
