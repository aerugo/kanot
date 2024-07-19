<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { clickOutside } from '../utils/helpers.ts';

  interface Option {
    id: number;
    name: string;
  }

  const dispatch = createEventDispatcher<{change: number[]}>();

  export let options: Option[] = [];
  export let selected: number[] = [];
  export let isOpen = false;
  export let label = 'Filter';

  let searchTerm = '';

  $: filteredOptions = options.filter(option => 
    option.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  function toggleSelection(optionId: number) {
    selected = selected.includes(optionId)
      ? selected.filter(id => id !== optionId)
      : [...selected, optionId];
    dispatch('change', selected);
  }

  function clearFilters() {
    selected = [];
    searchTerm = '';
    dispatch('change', selected);
  }

  function closeDropdown() {
    isOpen = false;
  }
</script>

<div 
  class="filter-container" 
  use:clickOutside={closeDropdown}
>
  <button class="filter-toggle" on:click={() => isOpen = !isOpen}>
    {label} {isOpen ? '▲' : '▼'}
  </button>
  {#if isOpen}
    <div class="filter-dropdown">
      <input 
        type="text" 
        bind:value={searchTerm} 
        placeholder="Search..." 
        class="filter-search"
      >
      <div class="filter-options">
        {#each filteredOptions as option}
          <label class="filter-option">
            <input 
              type="checkbox" 
              checked={selected.includes(option.id)} 
              on:change={() => toggleSelection(option.id)}
            >
            <span class="option-name" title={option.name}>{option.name}</span>
          </label>
        {/each}
      </div>
      {#if selected.length > 0}
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

  .option-name {
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
