<script>
  import { onDestroy, onMount } from "svelte";
  import FilterDropdown from "../components/FilterDropdown.svelte";
  import SearchBar from "../components/SearchBar.svelte";
  import SelectedFilters from "../components/SelectedFilters.svelte";
  import { codes } from "../stores/codeStore.js";
  import {
    fetchCodeTypes,
    fetchSegments,
    fetchSeries,
    searchElements,
  } from "../utils/api.js";
  import { debounce } from "../utils/helpers.js";

  let elements = [];
  let searchTerm = "";
  let series = [];
  let segments = [];
  let selectedSeries = [];
  let selectedSegments = [];
  let selectedCodes = [];
  let page = 1;
  let loading = false;
  let hasMore = true;

  // Debounced search function
  const debouncedSearch = debounce(async () => {
    if (searchTerm.length >= 3 || selectedSeries.length > 0 || selectedSegments.length > 0 || selectedCodes.length > 0) {
      page = 1;
      elements = [];
      hasMore = true;
      await loadMoreElements(
        searchTerm,
        selectedSeries,
        selectedSegments,
        selectedCodes
      );
    }
  }, 300);

  // Function to load initial data
  async function loadData() {
    series = (await fetchSeries()).map((s) => ({
      id: s.series_id,
      name: s.series_title,
    }));
    segments = (await fetchSegments()).map((s) => ({
      id: s.segment_id,
      name: s.segment_title,
    }));
    await fetchCodeTypes(); // Ensure code types are loaded into store
    await codes.refresh(); // Load codes into the store
    await loadMoreElements();
  }

  // Function to load more elements based on search and filters
  async function loadMoreElements(
    term = "",
    seriesIds = [],
    segmentIds = [],
    codeIds = []
  ) {
    if (loading || !hasMore) return;
    loading = true;
    try {
      const newElements = await searchElements(
        term,
        seriesIds,
        segmentIds,
        codeIds,
        page
      );
      if (newElements.length === 0) {
        hasMore = false;
      }
      elements = [...elements, ...newElements];
      page++;
    } catch (error) {
      console.error("Error loading more elements:", error);
    } finally {
      loading = false;
    }
  }

  // Function to reset search results
  function resetSearch() {
    page = 1;
    elements = [];
    hasMore = true;
    loadMoreElements(
      searchTerm,
      selectedSeries,
      selectedSegments,
      selectedCodes
    );
  }

  // Scroll handler to load more elements when scrolling to the bottom
  const handleScroll = debounce(() => {
    const bottom =
      window.innerHeight + window.scrollY >= document.body.offsetHeight - 500;
    if (bottom && hasMore) {
      loadMoreElements(
        searchTerm,
        selectedSeries,
        selectedSegments,
        selectedCodes
      );
    }
  }, 200);

  // Reactive statement to trigger debounced search when search term or filters change
  $: if (searchTerm.length >= 3 || selectedSeries.length > 0 || selectedSegments.length > 0 || selectedCodes.length > 0) {
    debouncedSearch();
  } else if (searchTerm.length === 0 && selectedSeries.length === 0 && selectedSegments.length === 0 && selectedCodes.length === 0) {
    resetSearch();
  }

  let scrollHandler;

  onMount(() => {
    loadData();
    scrollHandler = () => handleScroll();
    window.addEventListener("scroll", scrollHandler);
  });

  onDestroy(() => {
    if (scrollHandler) {
      window.removeEventListener("scroll", scrollHandler);
    }
  });

  // Event handlers for filters
  function handleSearch(event) {
    searchTerm = event.detail;
    resetSearch();
  }

  function handleSeriesChanged(event) {
    selectedSeries = event.detail;
    resetSearch();
  }

  function handleSegmentChanged(event) {
    selectedSegments = event.detail;
    resetSearch();
  }

  function handleCodesChanged(event) {
    selectedCodes = event.detail;
    resetSearch();
  }

  function clearFilter(id, type) {
    switch(type) {
      case 'series':
        selectedSeries = selectedSeries.filter(seriesId => seriesId !== id);
        break;
      case 'segment':
        selectedSegments = selectedSegments.filter(segmentId => segmentId !== id);
        break;
      case 'code':
        selectedCodes = selectedCodes.filter(codeId => codeId !== id);
        break;
    }
    resetSearch();
  }

  function clearAllFilters() {
    selectedSeries = [];
    selectedSegments = [];
    selectedCodes = [];
    resetSearch();
  }
</script>

<main>
  <h1>Content</h1>

  <div class="filters">
    <SearchBar
      bind:value={searchTerm}
      placeholder="Search element texts..."
      debounceDelay={300}
      on:search={handleSearch}
    />
    <FilterDropdown
      label="Filter by Series"
      options={series}
      bind:selected={selectedSeries}
      on:change={handleSeriesChanged}
    />
    <FilterDropdown
      label="Filter by Segment"
      options={segments}
      bind:selected={selectedSegments}
      on:change={handleSegmentChanged}
    />
    <FilterDropdown
      label="Filter by Code"
      options={$codes.map((code) => ({
        id: code.code_id,
        name: code.term,
      }))}
      bind:selected={selectedCodes}
      on:change={handleCodesChanged}
    />
  </div>

  <SelectedFilters
    selectedSeries={selectedSeries}
    selectedSegments={selectedSegments}
    selectedCodes={selectedCodes}
    seriesOptions={series}
    segmentOptions={segments}
    onClearFilter={clearFilter}
    onClearAll={clearAllFilters}
  />

  <table>
    <thead>
      <tr>
        <th>Series</th>
        <th>Segment</th>
        <th>Segment Title</th>
        <th>Element</th>
        <th>Codes</th>
      </tr>
    </thead>
    <tbody>
      {#each elements as element}
        <tr>
          <td>{element.segment?.series?.series_title || "N/A"}</td>
          <td>{element.segment?.segment_id || "N/A"}</td>
          <td>{element.segment?.segment_title || "N/A"}</td>
          <td>
            {element.element_text}
          </td>
          <td>
            {#each element.annotations as annotation}
              <span class="code-tag">
                {annotation.code?.term}
                <button class="remove-code">×</button>
              </span>
            {/each}
            <button class="add-code">+</button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>

  {#if loading}
    <p>Loading more elements...</p>
  {/if}

  {#if !hasMore}
    <p>No more elements to load.</p>
  {/if}
</main>

<style>
  .filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th,
  td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
  }

  th {
    background-color: #4a90e2;
    color: white;
  }

  .code-tag {
    background-color: #e0e0e0;
    border-radius: 4px;
    padding: 2px 4px;
    margin-right: 4px;
    font-size: 0.8em;
    display: inline-flex;
    align-items: center;
  }

  .remove-code,
  .add-code {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 0.8em;
    padding: 0 2px;
  }

  .add-code {
    background-color: #4a90e2;
    color: white;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
  }
</style>
