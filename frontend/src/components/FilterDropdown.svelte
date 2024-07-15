<script>
    import { createEventDispatcher } from 'svelte';
    import { codeTypes } from '../stores/codeStore.js';
    import { clickOutside } from '../utils/clickOutside.js';
  
    const dispatch = createEventDispatcher();
  
    export let selectedTypes = [];
    export let isOpen = false;
  
    let searchTerm = '';
  
    $: filteredTypes = $codeTypes.filter(type => 
      type.type_name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  
    function toggleTypeSelection(typeId) {
      selectedTypes = selectedTypes.includes(typeId)
        ? selectedTypes.filter(id => id !== typeId)
        : [...selectedTypes, typeId];
      dispatch('typesChanged', selectedTypes);
    }
  
    function clearFilters() {
      selectedTypes = [];
      searchTerm = '';
      dispatch('typesChanged', selectedTypes);
    }
  
    function closeDropdown() {
      isOpen = false;
    }
  </script>
  
  <div class="filter-container" use:clickOutside on:clickoutside={closeDropdown}>
    <button class="filter-toggle" on:click={() => isOpen = !isOpen}>
      Filter by Type {isOpen ? '▲' : '▼'}
    </button>
    {#if isOpen}
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
  
  <style>
    .filter-container {
      position: relative;
      display: inline-block;
    }
  
    .filter-toggle {
      background-color: #3498db;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      cursor: pointer;
      transition: background-color 0.3s ease;
    }
  
    .filter-toggle:hover {
      background-color: #2980b9;
    }
  
    .filter-dropdown {
      position: absolute;
      top: 100%;
      left: 0;
      background-color: white;
      border: 1px solid #ddd;
      border-radius: 4px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      z-index: 10;
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
      align-items: center;
      padding: 0.5rem;
      cursor: pointer;
    }
  
    .filter-option:hover {
      background-color: #f0f0f0;
    }
  
    .filter-option input[type="checkbox"] {
      margin-right: 0.5rem;
    }
  
    .type-name {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  
    .clear-filters {
      display: block;
      width: 100%;
      padding: 0.5rem;
      background-color: #e74c3c;
      color: white;
      border: none;
      cursor: pointer;
      transition: background-color 0.3s ease;
    }
  
    .clear-filters:hover {
      background-color: #c0392b;
    }
  </style>