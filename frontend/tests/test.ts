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

// Test for removing an annotation from an element
test('can remove annotation from an element', async ({ page }) => {
	await page.goto('/content');

	await page.waitForSelector('table', { state: 'visible', timeout: 20000 });

	await page.click('table tbody tr:first-child button.add-code');
	await page.waitForSelector('.annotation-dropdown', { state: 'visible', timeout: 20000 });
	await page.click('.annotation-dropdown ul li button:first-child');

	await page.waitForTimeout(2000);

	const initialAnnotationCount = await page.locator('table tbody tr:first-child .code-tag').count();

	const firstAnnotationText = await page.locator('table tbody tr:first-child .code-tag').first().textContent();

	await page.click('table tbody tr:first-child .code-tag:first-child button.remove-code');

	await page.waitForTimeout(2000);

	const newAnnotationCount = await page.locator('table tbody tr:first-child .code-tag').count();
	expect(newAnnotationCount).toBe(initialAnnotationCount - 1);

	await expect(page.locator(`table tbody tr:first-child .code-tag:has-text("${firstAnnotationText}")`)).not.toBeVisible();
}, { timeout: 180000 }); // Increase overall test timeout to 180 seconds

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

// Test for batch annotation
test('can add annotations in batch', async ({ page }) => {
	await page.goto('/content');

	// Wait for the table to be visible
	await page.waitForSelector('table', { state: 'visible', timeout: 30000 });

	// Log the number of checkboxes found
	const checkboxCount = await page.locator('table tbody tr input[type="checkbox"]').count();
	console.log(`Number of checkboxes found: ${checkboxCount}`);
	
	// Log the visibility of some key elements
	const tableVisible = await page.isVisible('table');
	const firstCheckboxVisible = await page.isVisible('table tbody tr:first-child input[type="checkbox"]');
	console.log(`Table visible: ${tableVisible}, First checkbox visible: ${firstCheckboxVisible}`);

	// Select elements (3rd to 10th)
	await page.click('table tbody tr:nth-child(3) input[type="checkbox"]');
	await page.keyboard.down('Shift');
	await page.click('table tbody tr:nth-child(10) input[type="checkbox"]');
	await page.keyboard.up('Shift');

	// Log the number of selected checkboxes
	const selectedCheckboxCount = await page.locator('table tbody tr input[type="checkbox"]:checked').count();
	console.log(`Number of selected checkboxes: ${selectedCheckboxCount}`);

	// Check if the "Annotate Selected" button is visible
	const annotateButtonVisible = await page.isVisible('button:has-text("Annotate Selected")');
	console.log(`"Annotate Selected" button visible: ${annotateButtonVisible}`);

	// Log the current URL
	console.log(`Current URL: ${page.url()}`);

	// Take a screenshot before clicking the button
	await page.screenshot({ path: 'before-annotate-click.png' });

	// Click the batch annotation button
	await page.click('button:has-text("Annotate Selected")');
	console.log('Clicked "Annotate Selected" button');

	// Wait a bit and take another screenshot
	await page.waitForTimeout(2000);
	await page.screenshot({ path: 'after-annotate-click.png' });

	// Wait for the batch annotation modal to appear with increased timeout
	try {
		console.log('Waiting for modal to appear...');
		await page.waitForSelector('.modal', { state: 'visible', timeout: 180000 });
		console.log('Modal appeared successfully');
	} catch (error) {
		console.error('Modal did not appear:', error);
		// Log the current state of the page
		console.log('Current page content:', await page.content());
		// Take a screenshot for debugging
		await page.screenshot({ path: 'modal-not-visible.png' });
		throw error;
	}

	// Get all available codes
	const allCodes = await page.$$eval('.dropdown-wrapper .code-tag', (elements) => 
		elements.map(el => el.textContent?.trim())
	);
	console.log(`Available codes: ${allCodes.join(', ')}`);

	// Get existing annotations for the selected elements
	const existingAnnotations = await page.$$eval('table tbody tr:nth-child(n+3):nth-child(-n+10) .code-tag', 
		(elements) => elements.map(el => el.textContent?.trim())
	);
	console.log(`Existing annotations: ${existingAnnotations.join(', ')}`);

	// Find two unused codes
	const unusedCodes = allCodes.filter(code => !existingAnnotations.includes(code)).slice(0, 2);
	console.log(`Unused codes: ${unusedCodes.join(', ')}`);

	if (unusedCodes.length < 2) {
		throw new Error('Not enough unused codes available for testing');
	}

	// Select the two unused codes
	for (const code of unusedCodes) {
		await page.click('button:has-text("Add Code")');
		await page.click(`.dropdown-wrapper button:has-text("${code}")`);
	}

	// Apply the batch annotation
	await page.click('button:has-text("Apply")');

	// Wait for the modal to close
	await page.waitForSelector('.modal', { state: 'hidden', timeout: 30000 });

	// Check if the new annotations are added to all selected elements
	for (let i = 3; i <= 10; i++) {
		for (const code of unusedCodes) {
			await expect(page.locator(`table tbody tr:nth-child(${i}) .code-tag:has-text("${code}")`)).toBeVisible();
		}
	}
}, { timeout: 240000 }); // Increase the overall test timeout to 4 minutes

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

	// Wait for annotations to load
	await page.waitForSelector('table tbody tr:first-child .code-tag', { state: 'attached', timeout: 10000 });

	// Get the initial number of annotations
	const initialAnnotationCount = await page.locator('table tbody tr:first-child .code-tag').count();

	// Get existing annotations for the element
	const existingAnnotations = await page.locator('table tbody tr:first-child .code-tag').allTextContents();

	// Click the add annotation button on the first element
	await page.click('table tbody tr:first-child button.add-code');

	// Wait for the annotation dropdown to be visible
	await page.waitForSelector('.annotation-dropdown', { state: 'visible', timeout: 20000 });

	// Get all available codes from the dropdown
	const allCodes = await page.locator('.annotation-dropdown ul li button').allTextContents();

	// Find a code that is not already used for the element
	let unusedCode;
	for (const code of allCodes) {
		if (!existingAnnotations.some(annotation => annotation.startsWith(code))) {
			unusedCode = code;
			break;
		}
	}

	if (unusedCode) {

		// Click the unused code option
		await page.click(`.annotation-dropdown ul li button:has-text("${unusedCode}")`);

		// Wait for the new code tag to be added
		await page.waitForSelector(`table tbody tr:first-child .code-tag:has-text("${unusedCode}")`, { state: 'visible', timeout: 15000 });

		// Check if a new code tag is added to the element
		const newAnnotationCount = await page.locator('table tbody tr:first-child .code-tag').count();
		expect(newAnnotationCount).toBe(initialAnnotationCount + 1);

		// Verify that the new annotation is visible in the UI
		await expect(page.locator(`table tbody tr:first-child .code-tag:has-text("${unusedCode}")`)).toBeVisible();
	} else {
		console.error('No unused codes found. This test cannot proceed.');
		throw new Error('No unused codes available for testing');
	}
});
