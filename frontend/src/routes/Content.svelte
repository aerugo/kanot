<script>
  import { onDestroy, onMount } from "svelte";
  import { slide } from "svelte/transition";
  import AnnotationDropdown from "../components/AnnotationDropdown.svelte";
  import BatchAnnotationModal from "../components/BatchAnnotationModal.svelte";
  import FilterDropdown from "../components/FilterDropdown.svelte";
  import SearchBar from "../components/SearchBar.svelte";
  import SelectedFilters from "../components/SelectedFilters.svelte";
  import { codes } from "../stores/codeStore.js";

  import {
    createAnnotation,
    deleteAnnotation,
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
  let annotationDropdownOpen = false;
  let activeElementId = null;
  let selectedElements = [];
  let selectAll = false;
  let showBatchAnnotationModal = false;

  // Debounced search function
  const debouncedSearch = debounce(async () => {
    if (
      searchTerm.length >= 3 ||
      selectedSeries.length > 0 ||
      selectedSegments.length > 0 ||
      selectedCodes.length > 0
    ) {
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
  $: if (
    searchTerm.length >= 3 ||
    selectedSeries.length > 0 ||
    selectedSegments.length > 0 ||
    selectedCodes.length > 0
  ) {
    debouncedSearch();
  } else if (
    searchTerm.length === 0 &&
    selectedSeries.length === 0 &&
    selectedSegments.length === 0 &&
    selectedCodes.length === 0
  ) {
    resetSearch();
  }

  let scrollHandler;

  onMount(() => {
    loadData();
    codes.refresh();
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
    switch (type) {
      case "series":
        selectedSeries = selectedSeries.filter((seriesId) => seriesId !== id);
        break;
      case "segment":
        selectedSegments = selectedSegments.filter(
          (segmentId) => segmentId !== id
        );
        break;
      case "code":
        selectedCodes = selectedCodes.filter((codeId) => codeId !== id);
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

  async function addAnnotation(event) {
    const { elementId, codeId } = event.detail;
    try {
      const newAnnotation = await createAnnotation({
        element_id: elementId,
        code_id: codeId,
      });

      if (newAnnotation) {
        elements = elements.map((element) => {
          if (element.element_id === elementId) {
            return {
              ...element,
              annotations: [...element.annotations, newAnnotation],
            };
          }
          return element;
        });
      } else {
        console.error("Failed to create annotation");
        // Optionally, show an error message to the user
      }
    } catch (error) {
      console.error("Error adding annotation:", error);
      // Optionally, show an error message to the user
    }
  }

  async function removeAnnotation(elementId, annotationId) {
    try {
      await deleteAnnotation(annotationId);
      const elementIndex = elements.findIndex(
        (el) => el.element_id === elementId
      );
      if (elementIndex !== -1) {
        elements[elementIndex].annotations = elements[
          elementIndex
        ].annotations.filter((a) => a.annotation_id !== annotationId);
        elements = [...elements];
      }
    } catch (error) {
      console.error("Error removing annotation:", error);
    }
  }

  function openAnnotationDropdown(elementId) {
    activeElementId = elementId;
    annotationDropdownOpen = true;
  }

  function toggleSelectAll() {
    selectAll = !selectAll;
    selectedElements = selectAll ? elements.map((e) => e.element_id) : [];
  }

  function toggleElementSelection(elementId) {
    if (selectedElements.includes(elementId)) {
      selectedElements = selectedElements.filter(id => id !== elementId);
    } else {
      selectedElements = [...selectedElements, elementId];
    }
  }

  function clearSelection() {
    selectedElements = [];
    // If you're using a selectAll checkbox, make sure to uncheck it
    selectAll = false;
  }

  function openBatchAnnotationModal() {
    showBatchAnnotationModal = true;
  }

  async function applyBatchAnnotations(event) {
    const { codeIds } = event.detail;
    // Implement batch annotation logic here
    console.log('Applying batch annotations', { elementIds: selectedElements, codeIds });
    // TODO: Call API to apply batch annotations
    // Reset selection after applying annotations
    clearSelection();
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
    {selectedSeries}
    {selectedSegments}
    {selectedCodes}
    seriesOptions={series}
    segmentOptions={segments}
    onClearFilter={clearFilter}
    onClearAll={clearAllFilters}
  />

  <table>
    <thead>
      <tr>
        <th>
          <input
            type="checkbox"
            bind:checked={selectAll}
            on:change={toggleSelectAll}
            aria-label="Select all elements"
          />
        </th>
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
          <td>
            <input
              type="checkbox"
              checked={selectedElements.includes(element.element_id)}
              on:change={() => toggleElementSelection(element.element_id)}
              aria-label={`Select element ${element.element_id}`}
            />
          </td>
          <td>{element.segment?.series?.series_title || "N/A"}</td>
          <td>{element.segment?.segment_id || "N/A"}</td>
          <td>{element.segment?.segment_title || "N/A"}</td>
          <td>{element.element_text}</td>
          <td>
            {#each element.annotations as annotation}
              <span class="code-tag">
                {annotation.code?.term}
                <button
                  class="remove-code"
                  on:click={() =>
                    removeAnnotation(
                      element.element_id,
                      annotation.annotation_id
                    )}>×</button
                >
              </span>
            {/each}
            <button
              class="add-code"
              on:click={() => openAnnotationDropdown(element.element_id)}
              >+</button
            >
            {#if annotationDropdownOpen && activeElementId === element.element_id}
              <AnnotationDropdown
                bind:isOpen={annotationDropdownOpen}
                elementId={element.element_id}
                on:select={addAnnotation}
              />
            {/if}
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

  {#if selectedElements.length > 0}
    <div class="selection-bar" transition:slide="{{ duration: 300, y: 100 }}">
      <span class="selection-count">{selectedElements.length} element{selectedElements.length !== 1 ? 's' : ''} selected</span>
      <button class="annotate-button" on:click={openBatchAnnotationModal}>
        Annotate Selected
      </button>
      <button class="clear-button" on:click={clearSelection}>
        Clear Selection
      </button>
    </div>
  {/if}

  <BatchAnnotationModal
  bind:show={showBatchAnnotationModal}
  selectedCount={selectedElements.length}
  on:applyAnnotations={applyBatchAnnotations}
/>
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
    display: inline-flex;
    align-items: center;
    background-color: #e0e0e0;
    border-radius: 4px;
    padding: 2px 4px;
    margin-right: 4px;
    font-size: 0.8em;
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

  .selection-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #f0f0f0;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
  }

  .selection-count {
    font-weight: bold;
  }

  .annotate-button, .clear-button {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  .annotate-button {
    background-color: #4a90e2;
    color: white;
  }

  .clear-button {
    background-color: transparent;
    color: #333;
  }

  .annotate-button:hover, .clear-button:hover {
    opacity: 0.8;
  }

  .annotate-button:focus, .clear-button:focus {
    outline: none;
    box-shadow: 0 0 0 2px #4a90e2;
  }

</style>
