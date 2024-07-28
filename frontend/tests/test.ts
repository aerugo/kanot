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
  
  await page.waitForSelector('.codes-list', { state: 'visible' });
  
  const initialCodeCount = await page.locator('.codes-list tr').count();
  
  await page.click('button:has-text("Filter by Type")');
  
  await page.waitForSelector('.filter-dropdown', { state: 'visible' });
  
  await page.click('.filter-option:first-child');
  
  await page.waitForTimeout(2000);
  
  const filteredCodeCount = await page.locator('.codes-list tr').count();
  
  // Check if the filter was applied successfully
  expect(filteredCodeCount).not.toBe(initialCodeCount);
  
  // Check for the presence of the filter tag
  const filterTag = page.locator('.active-filter');
  await expect(filterTag).toBeVisible();
  
  await expect(page.locator('.codes-list')).toBeVisible();
});
  
  // Test for editing a code
  test('can edit an existing code', async ({ page }) => {
    await page.goto('/codes');
    
    // Wait for the codes list to be visible and contain at least one row
    await page.waitForSelector('.codes-list tr', { state: 'visible', timeout: 5000 });

    // Log the number of rows in the codes list
    const rowCount = await page.locator('.codes-list tr').count();
    console.log(`Number of rows in codes list: ${rowCount}`);

    // Check if there's at least one row
    if (rowCount > 0) {
      // Wait for and click the edit button on the first code
      await page.waitForSelector('.codes-list tr:first-child button:has-text("Edit")', { state: 'visible', timeout: 15000 });
      await page.click('.codes-list tr:first-child button:has-text("Edit")');
      
      // Wait for the modal to appear
      await page.waitForSelector('.modal', { state: 'visible', timeout: 5000 });

      // Fill in new values for all fields
      await page.fill('[data-id="edit-code-term"]', 'TEST Updated Code Term');
      await page.fill('[data-id="edit-code-description"]', 'TEST Updated Code Description');
      
      // Select a specific code type option
      const codeTypeSelect = await page.waitForSelector('select', { state: 'visible', timeout: 5000 });
      if (codeTypeSelect) {
        await codeTypeSelect.selectOption({ index: 1 }); // Select the second option
        const selectedCodeType = await codeTypeSelect.evaluate(el => (el as HTMLSelectElement).selectedOptions[0].textContent);
        console.log(`Selected code type: ${selectedCodeType}`);
      } else {
        console.error('Code type select element not found');
      }
      
      await page.fill('[data-id="edit-code-reference"]', 'TEST Updated Reference');
      await page.fill('[data-id="edit-code-coordinates"]', 'TEST Updated Coordinates');

      // Save the changes
      await page.click('.modal button:has-text("Save")');
      
      console.log('Clicked Save button');

      // Wait for the save operation to complete (increase timeout if needed)
      await page.waitForTimeout(5000);

      // Check if the modal closes
      try {
        await expect(page.locator('.modal')).not.toBeVisible({ timeout: 20000 });
      } catch (error) {
        console.error('Modal did not close as expected:', error);
        // Log the current state of the modal
        const modalContent = await page.locator('.modal').innerHTML();
        console.log('Modal content:', modalContent);
        
        // Check if there are any error messages
        const errorMessages = await page.locator('.error-message').allInnerTexts();
        console.log('Error messages:', errorMessages);
        
        // Log the network requests
        const requests = await page.context().pages()[0].evaluate(() => {
          return (window as any).requestLog || [];
        });
        console.log('Network requests:', requests);

        // Log console messages
        const consoleMessages = await page.context().pages()[0].evaluate(() => {
          return (window as any).consoleLog || [];
        });
        console.log('Console messages:', consoleMessages);

        // Log the visibility state of the modal
        const isModalVisible = await page.locator('.modal').isVisible();
        console.log('Is modal visible:', isModalVisible);

        // Log any JavaScript errors
        const jsErrors = await page.evaluate(() => (window as any).jsErrors || []);
        console.log('JavaScript errors:', jsErrors);
        
        throw error;
      }

      console.log('Modal closed successfully');
      
      // Wait for the update to be reflected
      await page.waitForTimeout(2000);
      
      // Check if all updated fields are visible in the list
      await expect(page.locator('.codes-list')).toContainText('TEST Updated Code Term');
      await expect(page.locator('.codes-list')).toContainText('TEST Updated Code Description');
      await expect(page.locator('.codes-list')).toContainText('TEST Updated Reference');
      await expect(page.locator('.codes-list')).toContainText('TEST Updated Coordinates');
      
      // Click the edit button again to verify all fields
      await page.click('.codes-list tr:first-child button:has-text("Edit")');
      await page.waitForSelector('.modal', { state: 'visible', timeout: 5000 });
      
      // Verify all fields contain the updated values
      await expect(page.locator('[data-id="edit-code-term"]')).toHaveValue('TEST Updated Code Term');
      await expect(page.locator('[data-id="edit-code-description"]')).toHaveValue('TEST Updated Code Description');
      await expect(page.locator('[data-id="edit-code-reference"]')).toHaveValue('TEST Updated Reference');
      await expect(page.locator('[data-id="edit-code-coordinates"]')).toHaveValue('TEST Updated Coordinates');
      
      // Verify that the selected code type is still the same
      const updatedCodeTypeSelect = await page.waitForSelector('select', { state: 'visible', timeout: 5000 });
      if (updatedCodeTypeSelect) {
        const updatedCodeType = await updatedCodeTypeSelect.evaluate(el => (el as HTMLSelectElement).selectedOptions[0].textContent);
        console.log(`Updated code type: ${updatedCodeType}`);
      } else {
        console.error('Updated code type select element not found');
      }
      
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
	
	// Wait for the codes list to be visible
	await page.waitForSelector('.codes-list', { state: 'visible' });
	
	// Store the initial number of codes
	const initialCodeCount = await page.locator('.codes-list tr').count();
	
	// Click the delete button on the first code
	await page.click('.codes-list tr:first-child button:has-text("Delete")');
	
	// Confirm deletion in the modal
	await page.click('.modal button:has-text("Delete")');
	
	// Wait for the deletion to be reflected in the UI
	await page.waitForTimeout(2000);
	
	// Check if the number of codes has decreased
	const newCodeCount = await page.locator('.codes-list tr').count();
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
	await page.waitForSelector('table', { state: 'visible' });
	
	// Click the add annotation button on the first element
	await page.click('table tbody tr:first-child button.add-code');
	
	// Check if the annotation dropdown is visible
	await expect(page.locator('.annotation-dropdown')).toBeVisible();
	
	// Select the first code from the dropdown
	await page.click('.annotation-dropdown .filter-option:first-child');
	
	// Wait for the code tag to be added
	await page.waitForTimeout(1000);
	
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
    const afterAddAnnotationCount = await page.locator('table tbody tr:first-child .code-tag').count();
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
