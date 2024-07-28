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
	await page.waitForTimeout(1000);

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
	await expect(page.locator('form select')).toBeVisible();
});

// Test for filtering codes by type
test('can filter codes by type', async ({ page }) => {
	await page.goto('/codes');

	// Wait for at least one code to be present in the list
	await page.waitForSelector('.codes-list tr', { state: 'visible' });

	// Function to get the current code count
	const getCodeCount = async () => await page.locator('.codes-list tr').count();

	// Wait for the code count to stabilize
	let initialCodeCount = 0;
	const maxAttempts = 20;
	let attempts = 0;

	while (attempts < maxAttempts) {
		const currentCount = await getCodeCount();
		if (currentCount > 0 && currentCount === initialCodeCount) {
			break;
		}
		initialCodeCount = currentCount;
		await page.waitForTimeout(500);
		attempts++;
	}

	if (initialCodeCount === 0) {
		throw new Error('Failed to get initial code count after multiple attempts');
	}

	// Click the "Filter by Type" dropdown
	await page.click('button:has-text("Filter by Type")');

	// Wait for the dropdown options to be visible
	await page.waitForSelector('.filter-dropdown .filter-option', { state: 'visible' });

	// Select the first filter option
	await page.click('.filter-dropdown .filter-option:first-child');

	// Wait for the filter to be applied
	let filteredCodeCount = 0;
	const filterMaxAttempts = 20;
	let filterAttempts = 0;

	while (filterAttempts < filterMaxAttempts) {
		filteredCodeCount = await getCodeCount();
		if (filteredCodeCount !== initialCodeCount) {
			break;
		}
		await page.waitForTimeout(500);
		filterAttempts++;
	}

	expect(filteredCodeCount).not.toBe(initialCodeCount);

	// Check for the presence of the filter tag in SelectedFilters component
	const filterTag = page.locator('.selected-filters .filter-tag');
	await expect(filterTag).toBeVisible();

	// Check if the filter tag has the correct background color (assuming it's 'gray' for type filters)
	const filterTagColor = await filterTag.evaluate((el) => window.getComputedStyle(el).backgroundColor);
	expect(filterTagColor).toBe('rgb(128, 128, 128)'); // This is the RGB value for gray

	// Verify that the codes list is still visible
	await expect(page.locator('.codes-list')).toBeVisible();

	// Clear the filter
	await page.click('.selected-filters .filter-tag button');

	// Wait for the filter to be cleared and the list to update
	let finalCodeCount = 0;
	const clearMaxAttempts = 20;
	let clearAttempts = 0;

	while (clearAttempts < clearMaxAttempts) {
		finalCodeCount = await getCodeCount();
		if (finalCodeCount === initialCodeCount) {
			break;
		}
		await page.waitForTimeout(500);
		clearAttempts++;
	}

	// Ensure the filter is fully cleared
	const remainingFilterTags = await page.locator('.selected-filters .filter-tag').count();
	if (remainingFilterTags > 0) {
		await page.click('.selected-filters .clear-all-filters');
		await page.waitForTimeout(2000);
		
		// Wait again for the code count to stabilize
		await page.waitForFunction(
			({ initialCount, getCount }) => {
				return new Promise((resolve) => {
					const checkCount = async () => {
						const currentCount = await getCount();
						if (currentCount === initialCount) {
							resolve(true);
						} else {
							setTimeout(checkCount, 500);
						}
					};
					checkCount();
				});
			},
			{ initialCount: initialCodeCount, getCount: getCodeCount },
			{ timeout: 10000 }
		);
		
		finalCodeCount = await getCodeCount();
	}

	expect(finalCodeCount).toBe(initialCodeCount);
});

// Test for editing a code
test('can edit an existing code', async ({ page }) => {
	await page.goto('/codes');

	// Wait for the codes list to be visible and contain at least one row
	await page.waitForSelector('.codes-list tr', { state: 'visible', timeout: 5000 });

	// Log the number of rows in the codes list
	const rowCount = await page.locator('.codes-list tr').count();

	// Check if there's at least one row
	if (rowCount > 0) {
		// Wait for and click the edit button on the first code
		await page.waitForSelector('.codes-list tr:first-child button:has-text("Edit")', {
			state: 'visible',
			timeout: 2000
		});
		await page.click('.codes-list tr:first-child button:has-text("Edit")');

		// Wait for the modal to appear
		await page.waitForSelector('.modal', { state: 'visible', timeout: 2000 });

		// Fill in new values for all fields
		await page.fill('[data-id="edit-code-term"]', 'TEST Updated Code Term');
		await page.fill('[data-id="edit-code-description"]', 'TEST Updated Code Description');

		// Open the custom dropdown
		await page.click('[data-id="edit-code-type"] .selected-option');

		// Wait for the dropdown options to be visible
		await page.waitForSelector('[data-id="edit-code-type"] .options', { state: 'visible' });

		// Select the second option in the dropdown
		const options = await page.$$('[data-id="edit-code-type"] .option');
		if (options.length > 1) {
			await options[1].click();
		} else {
			throw new Error('Not enough options in the dropdown');
		}

		// Get the selected code type
		const selectedCodeType = await page
			.locator('[data-id="edit-code-type"] .selected-option')
			.textContent();

		// Wait for a short time to ensure the dropdown has closed
		await page.waitForTimeout(500);

		await page.fill('[data-id="edit-code-reference"]', 'TEST Updated Reference');
		await page.fill('[data-id="edit-code-coordinates"]', 'TEST Updated Coordinates');

		// Save the changes
		await page.click('.modal button:has-text("Save")');

		// Wait for the save operation to complete (increase timeout if needed)
		await page.waitForTimeout(1000);

		// Check if the modal closes
		try {
			await expect(page.locator('.modal')).not.toBeVisible({ timeout: 2000 });
		} catch (error) {
			console.error('Modal did not close as expected:', error);
			throw error;
		}

		// Wait for the update to be reflected
		await page.waitForTimeout(2000);

		// Check if all updated fields are visible in the list
		await expect(page.locator('.codes-list')).toContainText('TEST Updated Code Term');
		await expect(page.locator('.codes-list')).toContainText('TEST Updated Code Description');

		// Click the edit button again to verify all fields
		await page.click('.codes-list tr:first-child button:has-text("Edit")');
		await page.waitForSelector('.modal', { state: 'visible', timeout: 1000 });

		// Verify all fields contain the updated values
		await expect(page.locator('[data-id="edit-code-term"]')).toHaveValue('TEST Updated Code Term');
		await expect(page.locator('[data-id="edit-code-description"]')).toHaveValue(
			'TEST Updated Code Description'
		);
		await expect(page.locator('[data-id="edit-code-reference"]')).toHaveValue(
			'TEST Updated Reference'
		);
		await expect(page.locator('[data-id="edit-code-coordinates"]')).toHaveValue(
			'TEST Updated Coordinates'
		);

		// Close the modal
		await page.click('.modal button:has-text("Cancel")');
	} else {
		console.error('No codes found in the list');
		throw new Error('No codes found in the list');
	}
});

// Test for deleting a code
test('can delete a code', async ({ page }) => {
	await page.goto('/codes');

  // Wait for 2 seconds to ensure the page is loaded
  await page.waitForTimeout(2000);

	// Wait for the codes list to be visible
	await page.waitForSelector('.codes-list', { state: 'visible' });

	// Store the initial number of codes
	let initialCodeCount = await page.locator('.codes-list tr').count();

	// If there are no codes, create one
	if (initialCodeCount === 0) {
		await page.click('button:has-text("New Code")');
		await page.fill('input[placeholder="Term"]', 'Test Code');
		await page.fill('input[placeholder="Description"]', 'Test Description');
		await page.selectOption('select', { index: 0 }); // Select the first code type
		await page.click('button:has-text("Add Code")');
		await page.waitForTimeout(2000); // Wait for the new code to be added
		initialCodeCount = await page.locator('.codes-list tr').count();
	}

	// Click the delete button on the first code
	await page.click('.codes-list tr:first-child button:has-text("Delete")');

	// Confirm deletion in the modal
	await page.click('.modal button:has-text("Delete")');

	// Wait for the deletion to be reflected in the UI
	await page.waitForTimeout(2000);

	// Check if the number of codes has decreased
	const newCodeCount = await page.locator('.codes-list tr').count();

	if (newCodeCount >= initialCodeCount) {
		console.error(`Deletion failed. Initial count: ${initialCodeCount}, New count: ${newCodeCount}`);
		// Take a screenshot for debugging
		await page.screenshot({ path: 'deletion-failed.png' });
	}

	expect(newCodeCount).toBe(initialCodeCount - 1);
});

// Test for pagination on the Content page
test('content pagination loads more items', async ({ page }) => {
	await page.goto('/content');

	// Wait for the table to be visible
	await page.waitForSelector('table', { state: 'visible' });

	// Get the initial number of rows
	const initialRowCount = await page.locator('table tbody tr').count();

	// Scroll to the bottom of the page to trigger loading more items
	await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

	// Wait for new items to load (adjust timeout as needed)
	await page.waitForTimeout(2000);

	// Check if the number of rows has increased
	const newRowCount = await page.locator('table tbody tr').count();
	expect(newRowCount).toBeGreaterThan(initialRowCount);
});

// Test for adding an annotation to an element
test('can add annotation to an element', async ({ page }) => {
	await page.goto('/content');

	// Wait for the table to be visible
	await page.waitForSelector('table', { state: 'visible', timeout: 15000 });

	// Click the add annotation button on the first element
	await page.click('table tbody tr:first-child button.add-code');

	// Wait for the annotation dropdown to be visible
	await page.waitForSelector('.annotation-dropdown', { state: 'visible', timeout: 20000 });

	// Check if the annotation dropdown is visible
	await expect(page.locator('.annotation-dropdown')).toBeVisible();

	// Log the current state of the dropdown
	console.log('Dropdown HTML:', await page.locator('.annotation-dropdown').evaluate(el => el.outerHTML));

	// Wait for the filter options to be visible
	await page.waitForSelector('.annotation-dropdown .filter-option', { state: 'visible', timeout: 20000 });

	// Log the number of filter options found
	const filterOptionsCount = await page.locator('.annotation-dropdown .filter-option').count();
	console.log('Number of filter options found:', filterOptionsCount);

	// Ensure that at least one filter option is present
	await expect(page.locator('.annotation-dropdown .filter-option')).toHaveCount({ min: 1 });

	// If filter options are found, click the first one
	if (filterOptionsCount > 0) {
		await page.click('.annotation-dropdown .filter-option:first-child', { timeout: 10000 });
	} else {
		throw new Error('No filter options found in the dropdown');
	}

	// Wait for the code tag to be added
	await page.waitForSelector('table tbody tr:first-child .code-tag', { state: 'visible', timeout: 15000 });

	// Check if a new code tag is added to the element
	await expect(page.locator('table tbody tr:first-child .code-tag')).toBeVisible();
});

// Test for adding and removing an annotation from an element
test('can add and remove annotation from an element', async ({ page }) => {
	await page.goto('/content');

	// Wait for the table to be visible
	await page.waitForSelector('table', { state: 'visible' });

	// Get the initial number of annotations
	const initialAnnotationCount = await page.locator('table tbody tr:first-child .code-tag').count();

	// Add an annotation
	await page.click('table tbody tr:first-child button.add-code');

	await page.waitForSelector('.annotation-dropdown', { state: 'visible' });

	await page.click('.annotation-dropdown .filter-option:first-child');

	// Wait for the code tag to appear
	await page.waitForSelector('table tbody tr:first-child .code-tag', { state: 'visible' });

	// Check if the number of annotations has increased
	const afterAddAnnotationCount = await page
		.locator('table tbody tr:first-child .code-tag')
		.count();
	expect(afterAddAnnotationCount).toBe(initialAnnotationCount + 1);

	// Remove the first annotation
	const removeButton = await page.locator('table tbody tr:first-child .code-tag button').first();
	await removeButton.click();

	// Wait for the annotation to be removed
	await page.waitForTimeout(2000);

	// Check if the number of annotations has decreased back to the initial count
	const finalAnnotationCount = await page.locator('table tbody tr:first-child .code-tag').count();
	expect(finalAnnotationCount).toBe(initialAnnotationCount);
});
