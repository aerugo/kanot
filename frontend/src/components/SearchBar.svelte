<script>
  import { debounce } from 'lodash-es';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  export let placeholder = 'Search...'; // Default placeholder
  export let debounceDelay = 300; // Default debounce delay
  export let value = ''; // Add this line to accept the 'value' prop

  const debouncedSearch = debounce((term) => {
    dispatch('search', term);
  }, debounceDelay);

  function handleSearch(event) {
    value = event.target.value; // Update the value prop
    debouncedSearch(value);
  }

  function clearSearch() {
    value = '';
    dispatch('search', '');
  }
</script>

<div class="search-container">
  <input
    type="text"
    {placeholder}
    bind:value={value} 
    on:input={handleSearch}
    aria-label={placeholder}
  />
  {#if value}
    <button class="clear-search" on:click={clearSearch} aria-label="Clear search">×</button>
  {/if}
</div>

<style>
  .search-container {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
    position: relative;
  }

  input {
    width: 100%;
    padding: 0.5rem;
    padding-right: 2rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  .clear-search {
    position: absolute;
    right: 0.5rem;
    background: none;
    border: none;
    color: #777;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 1.5rem;
    height: 1.5rem;
  }

  .clear-search:hover {
    color: #333;
  }
</style>
