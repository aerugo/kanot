<script>
    import { codeTypes } from "../stores/codeStore.js";
    export let selectedTypes = [];
    export let onClearFilter;
    export let onClearAll;
  
    $: selectedTypeNames = selectedTypes.map(typeId => {
      const type = $codeTypes.find(t => t.type_id === typeId);
      return type ? { id: type.type_id, name: type.type_name } : null;
    }).filter(Boolean);
  </script>
  
  <div class="selected-filters">
    {#each selectedTypeNames as type}
      <span class="filter-tag">
        {type.name}
        <button on:click={() => onClearFilter(type.id)}>×</button>
      </span>
    {/each}
    {#if selectedTypes.length > 1}
      <button class="clear-all-filters" on:click={onClearAll}>Clear All</button>
    {/if}
  </div>
  
  <style>
    .selected-filters {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }
  
    .filter-tag {
      background-color: #e0e0e0;
      border-radius: 16px;
      padding: 0.25rem 0.5rem;
      display: flex;
      align-items: center;
      font-size: 0.9rem;
    }
  
    .filter-tag button {
      background: none;
      border: none;
      color: #666;
      font-size: 1rem;
      cursor: pointer;
      padding: 0 0.25rem;
      margin-left: 0.25rem;
    }
  
    .clear-all-filters {
      background-color: #f0f0f0;
      border: none;
      border-radius: 16px;
      padding: 0.25rem 0.5rem;
      cursor: pointer;
      font-size: 0.9rem;
    }
  </style>