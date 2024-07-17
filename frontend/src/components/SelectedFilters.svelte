<script>
  import { codes } from "../stores/codeStore.js";
  
  export let selectedSeries = [];
  export let selectedSegments = [];
  export let selectedCodes = [];
  export let seriesOptions = [];
  export let segmentOptions = [];
  export let onClearFilter;
  export let onClearAll;

  $: selectedSeriesNames = selectedSeries.map(id => {
    const series = seriesOptions.find(s => s.id === id);
    return series ? { id: series.id, name: series.name, type: 'series' } : null;
  }).filter(Boolean);

  $: selectedSegmentNames = selectedSegments.map(id => {
    const segment = segmentOptions.find(s => s.id === id);
    return segment ? { id: segment.id, name: segment.name, type: 'segment' } : null;
  }).filter(Boolean);

  $: selectedCodeNames = selectedCodes.map(codeId => {
    const code = $codes.find(c => c.code_id === codeId);
    return code ? { id: code.code_id, name: code.term, type: 'code' } : null;
  }).filter(Boolean);

  $: allSelectedFilters = [...selectedSeriesNames, ...selectedSegmentNames, ...selectedCodeNames];

  function getFilterColor(type) {
    switch(type) {
      case 'series': return 'orange';
      case 'segment': return 'green';
      case 'code': return 'blue';
      default: return 'gray';
    }
  }
</script>

<div class="selected-filters">
  {#each allSelectedFilters as filter}
    <span class="filter-tag" style="background-color: {getFilterColor(filter.type)}">
      {filter.name}
      <button on:click={() => onClearFilter(filter.id, filter.type)}>×</button>
    </span>
  {/each}
  {#if allSelectedFilters.length > 1}
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
    border-radius: 16px;
    padding: 0.25rem 0.5rem;
    display: flex;
    align-items: center;
    font-size: 0.9rem;
    color: white;
  }

  .filter-tag button {
    background: none;
    border: none;
    color: white;
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