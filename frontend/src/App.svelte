<script>
  import axios from 'axios';
  import { onMount } from 'svelte';
  import { clickOutside } from './clickOutside.js';

  let codes = [];
  let codeTypes = [];
  let filteredCodes = [];

  let newCode = { term: '', description: '', type_id: '', reference: '', coordinates: '' };
  let editingCode = null;
  let statusMessage = '';
  let statusType = '';

  onMount(async () => {
    await fetchCodes();
    await fetchCodeTypes();
  });

  let selectedTypes = [];
  let isFilterOpen = false;
  let searchTerm = '';

  $: filteredTypes = codeTypes.filter(type => 
    type.type_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  $: {
    filteredCodes = codes.filter(code => 
      selectedTypes.length === 0 || selectedTypes.includes(code.code_type?.type_id)
    );
  }

  $: selectedTypeNames = selectedTypes.map(typeId => {
    const type = codeTypes.find(t => t.type_id === typeId);
    return type ? { id: type.type_id, name: type.type_name } : null;
  }).filter(Boolean);

  function toggleFilter() {
    isFilterOpen = !isFilterOpen;
    if (isFilterOpen) {
      searchTerm = '';
    }
  }

  function toggleTypeSelection(typeId) {
    selectedTypes = selectedTypes.includes(typeId)
      ? selectedTypes.filter(id => id !== typeId)
      : [...selectedTypes, typeId];
    console.log('Selected Types after toggle:', selectedTypes);
  }

  function clearFilters() {
    selectedTypes = [];
    searchTerm = '';
    isFilterOpen = false;
    setTimeout(() => isFilterOpen = true, 0);
  }

  function getDomain(url) {
    if (!url) return '';
    try {
      const domain = new URL(url).hostname;
      // remove subdomain and toplevel domain
      const site = domain.split('.').slice(-2).join('.').split('.')[0];
      return site.replace('www.', '').toLowerCase();
    } catch (e) {
      return url;
    }
  }

  function generateGoogleMapsLink(coordinateString) {
    const coordinateRegex = /^-?\d+(\.\d+)?,-?\d+(\.\d+)?$/;
    const strippedCoordinateString = coordinateString.replace(/\s+/g, ''); // Remove all spaces
    if (coordinateRegex.test(strippedCoordinateString)) {
      const [latitude, longitude] = strippedCoordinateString.split(',');
      return `https://www.google.com/maps?q=${latitude},${longitude}`;
    } else {
      return '';
    }
  }
  
  async function fetchCodes() {
    const response = await axios.get('http://localhost:8000/codes/');
    codes = response.data;
  }

  async function fetchCodeTypes() {
    const response = await axios.get('http://localhost:8000/code_types/');
    codeTypes = response.data;
    codeTypes = codeTypes.sort((a, b) => a.type_name.localeCompare(b.type_name));
  }

  async function addCode() {
    try {
      const response = await axios.post('http://localhost:8000/codes/', newCode);
      if (response.status === 200) {
        await fetchCodes();
        newCode = { term: '', description: '', type_id: '', reference: '', coordinates: '' };
        statusMessage = 'Code added successfully!';
        statusType = 'success';
      } else {
        statusMessage = response.data.message || "An error occurred while adding the code";
        statusType = 'error';
      }
    } catch (error) {
      if (error.response) {
        statusMessage = error.response.data.message || "An error occurred while adding the code";
      } else if (error.request) {
        statusMessage = "No response received from the server. Please check your connection.";
      } else {
        statusMessage = "An unexpected error occurred";
      }
      statusType = 'error';
    }
    setTimeout(() => {
      statusMessage = '';
      statusType = '';
    }, 5000);
  }

  function confirmDelete(id) {
    if (confirm("Are you sure you want to delete this code?")) {
      deleteCode(id);
    }
  }
  
  function startEditing(code) {
    editingCode = { ...code };
  }

  async function saveEdit() {
    await axios.put(`http://localhost:8000/codes/${editingCode.code_id}`, editingCode);
    editingCode = null;
    await fetchCodes();
  }

  async function deleteCode(id) {
    await axios.delete(`http://localhost:8000/codes/${id}`);
    await fetchCodes();
  }

  let sortColumn = 'term';
  let sortOrder = 'asc';

  function sortCodes(column) {
    if (sortColumn === column) {
      sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
      sortColumn = column;
      sortOrder = 'asc';
    }

    codes = codes.sort((a, b) => {
      let valueA, valueB;

      if (column === 'term') {
        valueA = a.term.toLowerCase();
        valueB = b.term.toLowerCase();
      } else if (column === 'type') {
        valueA = a.code_type?.type_name.toLowerCase() || '';
        valueB = b.code_type?.type_name.toLowerCase() || '';
      }

      if (valueA < valueB) return sortOrder === 'asc' ? -1 : 1;
      if (valueA > valueB) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }

</script>

<main>
  <h1>Kanot Code Management</h1>

  <section class="add-code">
    <h2>Add New Code</h2>
    {#if statusMessage}
      <div class="status-message {statusType}">
        {statusMessage}
      </div>
    {/if}
    <form on:submit|preventDefault={addCode}>
      <input bind:value={newCode.term} placeholder="Term" required>
      <input bind:value={newCode.description} placeholder="Description">
      <select bind:value={newCode.type_id} required>
        <option value="">Select Code Type</option>
        {#each codeTypes as codeType}
          <option value={codeType.type_id}>{codeType.type_name}</option>
        {/each}
      </select>
      <input bind:value={newCode.reference} placeholder="Read more">
      <input bind:value={newCode.coordinates} placeholder="Coordinates">
      <button type="submit">Add Code</button>
    </form>
  </section>

  <section class="codes-list">
    <h2>Codes List</h2>
    <div class="filter-container" use:clickOutside on:clickoutside={() => isFilterOpen = false}>
      <button class="filter-toggle" on:click={toggleFilter}>
        Filter by Type {isFilterOpen ? '▲' : '▼'}
      </button>
      {#if isFilterOpen}
      <div class="filter-dropdown">
        <input 
          type="text" 
          bind:value={searchTerm} 
          placeholder="Search types..." 
          class="filter-search"
        >
        <div class="filter-options">
          {#each filteredTypes as type}
            <label class="filter-option">
              <input 
                type="checkbox" 
                checked={selectedTypes.includes(type.type_id)} 
                on:change={() => toggleTypeSelection(type.type_id)}
              >
              <span class="type-name" title={type.type_name}>{type.type_name}</span>
            </label>
          {/each}
        </div>
        {#if selectedTypes.length > 0}
          <button class="clear-filters" on:click={clearFilters}>Clear Filters</button>
        {/if}
      </div>
      {/if}
      </div>
  {#if selectedTypes.length > 0}
    <div class="selected-filters">
      {#each selectedTypeNames as type}
        <span class="filter-tag">
          {type.name}
          <button on:click={() => toggleTypeSelection(type.id)}>×</button>
        </span>
      {/each}
      {#if selectedTypes.length > 1}
        <button class="clear-all-filters" on:click={clearFilters}>Clear All</button>
      {/if}
    </div>
  {/if}
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th on:click={() => sortCodes('term')}>
              Term {#if sortColumn === 'term'}{sortOrder === 'asc' ? '▲' : '▼'}{/if}
            </th>
            <th>Description</th>
            <th on:click={() => sortCodes('type')}>
              Type {#if sortColumn === 'type'}{sortOrder === 'asc' ? '▲' : '▼'}{/if}
            </th>
            <th>Read more</th>
            <th>Coordinates</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each filteredCodes as code (code.code_id)}
            <tr>
              <td>{code.term}</td>
              <td>{code.description}</td>
              <td>{code.code_type?.type_name || 'N/A'}</td>
              <td>
                {#if code.reference}
                  <a href={code.reference} target="_blank" rel="noopener noreferrer">
                    {getDomain(code.reference)}
                  </a>
                {/if}
              </td>
              <td>
                {#if code.coordinates}
                  <a href={generateGoogleMapsLink(code.coordinates)} target="_blank" rel="noopener noreferrer">
                    map
                  </a>
                {/if}
              </td>
              <td class="actions">
                <button on:click={() => startEditing(code)}>Edit</button>
                <button class="delete-btn" on:click={() => confirmDelete(code.code_id)}>Delete</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </section>

  {#if editingCode}
    <div class="modal-overlay">
      <div class="modal">
        <h2>Edit Code</h2>
        <form on:submit|preventDefault={saveEdit}>
          <input bind:value={editingCode.term} placeholder="Term" required>
          <input bind:value={editingCode.description} placeholder="Description">
          <select bind:value={editingCode.type_id} required>
            <option value="">Select Code Type</option>
            {#each codeTypes as codeType}
              <option value={codeType.type_id}>{codeType.type_name}</option>
            {/each}
          </select>
          <input bind:value={editingCode.reference} placeholder="Reference">
          <input bind:value={editingCode.coordinates} placeholder="Coordinates">
          <div class="button-group">
            <button type="submit">Save</button>
            <button type="button" on:click={() => editingCode = null}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  {/if}
</main>

<style>
  :global(body) {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f9f9f9;
    margin: 0;
    padding: 0;
  }

  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  h1, h2 {
    color: #2c3e50;
  }

  h1 {
    font-size: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
  }

  h2 {
    font-size: 1.8rem;
    margin-bottom: 1rem;
  }

  .add-code, .codes-list {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 2rem;
    margin-bottom: 2rem;
  }

  form {
    display: grid;
    gap: 1rem;
  }


  .status-message {
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 10px;
  }

  .status-message.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }

  .status-message.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }

  input, select {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  select {
    background-color: white;
    cursor: pointer;
  }

  select:focus {
    outline: none;
    border-color: #3498db;
  }

  button {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }

  .delete-btn {
    background-color: #e74c3c;
  }

  .delete-btn:hover {
    background-color: #c0392b;
  }

  .clear-filters {
    margin: 0.5rem;
  }

  button:hover {
    background-color: #2980b9;
  }

  .table-container {
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
  }

  th, td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #ecf0f1;
  }

  th {
    background-color: #3498db;
    color: white;
    font-weight: bold;
  }

  tr:nth-child(even) {
    background-color: #f8f9fa;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
  }

  .actions button {
    font-size: 0.8rem;
    padding: 0.3rem 0.6rem;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .modal {
    background-color: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    max-width: 500px;
    width: 100%;
  }

  .button-group {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
  }

  .filter-dropdown {
    position: absolute;
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    z-index: 20;
    width: 300px;
    max-height: 400px;
    overflow-y: auto;
  }

  .filter-search {
    width: 100%;
    padding: 0.5rem;
    border: none;
    border-bottom: 1px solid #ddd;
    box-sizing: border-box;
  }

  .filter-options {
    max-height: 300px;
    overflow-y: auto;
  }

  .filter-option {
    display: flex;
    align-items: left;
    padding: 0.5rem;
    cursor: pointer;
  }

  .filter-option:hover {
    background-color: #f0f0f0;
  }

  .filter-option input[type="checkbox"] {
    margin-right: 0.5rem;
    flex-shrink: 0;
  }

  .type-name {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex-grow: 1;
  }

  .filter-tag {
    margin-left: 0.5rem;
  }
  
</style>