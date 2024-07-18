<script>
  // Import statements
  import { onDestroy, onMount } from "svelte";
  import { writable } from "svelte/store";
  import { slide } from "svelte/transition";
// Component imports
  import AnnotationDropdown from "../components/AnnotationDropdown.svelte";
  import BatchAnnotationModal from "../components/BatchAnnotationModal.svelte";
  import FilterDropdown from "../components/FilterDropdown.svelte";
  import SearchBar from "../components/SearchBar.svelte";
  import SelectedFilters from "../components/SelectedFilters.svelte";
// Store imports
  import { codes } from "../stores/codeStore.js";
  import {
    filteredElements,
    loadMoreElements,
    searchTerm,
    selectedCodes,
    selectedSegments,
    selectedSeries,
  } from "../stores/elementStore.js";
// API function imports

  import {
    createAnnotation,
    createBatchAnnotations,
    deleteAnnotation,
    fetchCodeTypes,
    fetchSegments,
    fetchSeries,
  } from "../utils/api.js";
  // Helper function imports

  import { debounce } from "../utils/helpers.js";

  // Local state variables

  let elementsStore = writable([]);
  let page = 1;
  let loading = false;
  let hasMore = true;
  let annotationDropdownOpen = false;
  let activeElementId = null;
  let selectedElements = [];
  let showBatchAnnotationModal = false;
  let seriesOptions = [];
  let segmentOptions = [];
  let rangeStartIndex = -1;

  // Reactive statement to update elementsStore

  $: $elementsStore = $filteredElements;

  // Debounced search function

  const debouncedSearch = debounce(async () => {
    if (
      $searchTerm.length >= 3 ||
      $selectedSeries.length > 0 ||
      $selectedSegments.length > 0 ||
      $selectedCodes.length > 0
    ) {
      resetSearch();
    }
  }, 300);

  // Function to load initial data

  async function loadInitialData() {
    await loadFilterOptions();
    await fetchCodeTypes();
    await loadMoreData();
  }

  async function loadFilterOptions() {
    const [seriesData, segmentsData] = await Promise.all([
      fetchSeries(),
      fetchSegments(),
    ]);

    seriesOptions = seriesData.map((s) => ({
      id: s.series_id,
      name: s.series_title,
    }));

    segmentOptions = segmentsData.map((s) => ({
      id: s.segment_id,
      name: s.segment_title,
    }));
  }

  // Function to load more data

  async function loadMoreData() {
    if (loading || !hasMore) return;
    loading = true;
    try {
      const newElements = await loadMoreElements(
        page,
        $searchTerm,
        $selectedSeries,
        $selectedSegments,
        $selectedCodes
      );
      elementsStore.update((currentElements) => {
        const updatedElements = page === 1 ? newElements : [...currentElements, ...newElements];
        return updatedElements;
      });
      hasMore = newElements.length > 0;
      page++;
    } catch (error) {
      console.error("Error loading more elements:", error);
    } finally {
      loading = false;
    }
  }

  // Function to reset search results

  async function resetSearch() {
    page = 1;
    elementsStore.set([]);
    hasMore = true;
    await loadMoreData();
  }

  // Debounced reset search function

  const debouncedResetSearch = debounce(async () => {
    page = 1;
    elementsStore.set([]);
    hasMore = true;
    await loadMoreData();
  }, 300);

  // Scroll handler to load more elements when scrolling to the bottom

  const debouncedHandleScroll = debounce(() => {
    const bottom =
      window.innerHeight + window.scrollY >=
      document.documentElement.scrollHeight - 500;
    if (bottom && !loading && hasMore) {
      loadMoreData();
    }
  }, 200);

  function handleScroll() {
    debouncedHandleScroll();
  }

  onMount(async () => {
    await loadInitialData();
    codes.refresh();
    window.addEventListener("scroll", handleScroll);
  });

  onDestroy(() => {
    window.removeEventListener("scroll", handleScroll);
  });

  // Reactive statement for search and filters

  $: if (
    $searchTerm.length >= 3 ||
    $selectedSeries.length > 0 ||
    $selectedSegments.length > 0 ||
    $selectedCodes.length > 0
  ) {
    debouncedSearch();
  } else if (
    $searchTerm.length === 0 &&
    $selectedSeries.length === 0 &&
    $selectedSegments.length === 0 &&
    $selectedCodes.length === 0
  ) {
    debouncedResetSearch();
  }

  // Event handlers for filters

  function handleSearch(event) {
    $searchTerm = event.detail;
    resetSearch();
  }

  function handleSeriesChanged(event) {
    selectedSeries.set(event.detail);
    resetSearch();
  }

  function handleSegmentChanged(event) {
    selectedSegments.set(event.detail);
    resetSearch();
  }

  function handleCodesChanged(event) {
    selectedCodes.set(event.detail);
    resetSearch();
  }

  function clearFilter(id, type) {
    switch (type) {
      case "series":
        selectedSeries.update((series) =>
          series.filter((seriesId) => seriesId !== id)
        );
        break;
      case "segment":
        selectedSegments.update((segments) =>
          segments.filter((segmentId) => segmentId !== id)
        );
        break;
      case "code":
        selectedCodes.update((codes) =>
          codes.filter((codeId) => codeId !== id)
        );
        break;
    }
    resetSearch();
  }

  function clearAllFilters() {
    selectedSeries.set([]);
    selectedSegments.set([]);
    selectedCodes.set([]);
    resetSearch();
  }

  // Annotation functions

  async function addAnnotation(event) {
    const { elementId, codeId } = event.detail;
    try {
      const newAnnotation = await createAnnotation({
        element_id: elementId,
        code_id: codeId,
      });

      if (newAnnotation) {
        elementsStore.update((elements) =>
          elements.map((element) => {
            if (element.element_id === elementId) {
              return {
                ...element,
                annotations: [...element.annotations, newAnnotation],
              };
            }
            return element;
          })
        );
      } else {
        console.error("Failed to create annotation");
      }
    } catch (error) {
      console.error("Error adding annotation:", error);
    }
  }

  async function removeAnnotation(elementId, annotationId) {
    try {
      await deleteAnnotation(annotationId);
      elementsStore.update((elements) => {
        const elementIndex = elements.findIndex(
          (el) => el.element_id === elementId
        );
        if (elementIndex !== -1) {
          const updatedElement = {
            ...elements[elementIndex],
            annotations: elements[elementIndex].annotations.filter(
              (a) => a.annotation_id !== annotationId
            ),
          };
          return [
            ...elements.slice(0, elementIndex),
            updatedElement,
            ...elements.slice(elementIndex + 1),
          ];
        }
        return elements;
      });
    } catch (error) {
      console.error("Error removing annotation:", error);
    }
  }

  function openAnnotationDropdown(elementId) {
    activeElementId = elementId;
    annotationDropdownOpen = true;
  }

  // Element selection functions

  function handleElementSelection(index, elementId, event) {

    let newSelectedElements;

    if (event.shiftKey && rangeStartIndex !== -1) {
      const start = Math.min(rangeStartIndex, index);
      const end = Math.max(rangeStartIndex, index);

      newSelectedElements = [
        ...new Set([
          ...selectedElements,
          ...$elementsStore.slice(start, end + 1).map((e) => e.element_id),
        ]),
      ];
    } else {
      newSelectedElements = selectedElements.includes(elementId)
        ? selectedElements.filter((id) => id !== elementId)
        : [...selectedElements, elementId];

      rangeStartIndex = newSelectedElements.includes(elementId) ? index : -1;
    }

    // Update selectedElements
    selectedElements = newSelectedElements;
  }

  function clearSelection() {
    selectedElements = [];
  }

  // Batch annotation functions

  function openBatchAnnotationModal() {
    showBatchAnnotationModal = true;
  }

  async function applyBatchAnnotations(event) {
    const { codeIds } = event.detail;
    try {
      const newAnnotations = await createBatchAnnotations(
        selectedElements,
        codeIds
      );

      elementsStore.update((elements) =>
        elements.map((element) => {
          if (selectedElements.includes(element.element_id)) {
            const elementNewAnnotations = newAnnotations.filter(
              (annotation) => annotation.element_id === element.element_id
            );
            return {
              ...element,
              annotations: [...element.annotations, ...elementNewAnnotations],
            };
          }
          return element;
        })
      );

      clearSelection();
    } catch (error) {
      console.error("Error applying batch annotations:", error);
    }
  }
</script>

<!-- HTML structure -->

<main>
  <h1>Content</h1>

  <!-- Filters section -->

  <div class="filters">
    <SearchBar
      value={$searchTerm}
      on:input={(e) => searchTerm.set(e.target.value)}
      placeholder="Search element texts..."
      debounceDelay={300}
      on:search={handleSearch}
    />
    <FilterDropdown
      label="Filter by Series"
      options={seriesOptions}
      selected={$selectedSeries}
      on:change={handleSeriesChanged}
    />
    <FilterDropdown
      label="Filter by Segment"
      options={segmentOptions}
      selected={$selectedSegments}
      on:change={handleSegmentChanged}
    />
    <FilterDropdown
      label="Filter by Code"
      options={$codes.map((code) => ({
        id: code.code_id,
        name: code.term,
      }))}
      selected={$selectedCodes}
      on:change={handleCodesChanged}
    />
  </div>

  <!-- Selected filters display -->

  <SelectedFilters
    selectedSeries={$selectedSeries}
    selectedSegments={$selectedSegments}
    selectedCodes={$selectedCodes}
    {seriesOptions}
    {segmentOptions}
    onClearFilter={clearFilter}
    onClearAll={clearAllFilters}
  />

  <!-- Main content table -->
  <table class:loading>
    <thead>
      <tr>
        <th>Select</th>
        <th>Series</th>
        <th>Segment</th>
        <th>Segment Title</th>
        <th>Element</th>
        <th>Codes</th>
      </tr>
    </thead>
    <tbody>
      {#each $elementsStore as element, index}
        <tr>
          <td>
            <input
              type="checkbox"
              checked={selectedElements.includes(element.element_id)}
              on:click={(event) =>
                handleElementSelection(index, element.element_id, event)}
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

  <!-- Loading and "No more elements" messages -->

  {#if loading}
    <p>Loading more elements...</p>
  {/if}

  {#if !hasMore}
    <p>No more elements to load.</p>
  {/if}

  <!-- Selection bar for batch annotation -->

  {#if selectedElements.length > 0}
    <div class="selection-bar" transition:slide={{ duration: 300, y: 100 }}>
      <span class="selection-count"
        >{selectedElements.length} element{selectedElements.length !== 1
          ? "s"
          : ""} selected</span
      >
      <button class="annotate-button" on:click={openBatchAnnotationModal}>
        Annotate Selected
      </button>
      <button class="clear-button" on:click={clearSelection}>
        Clear Selection
      </button>
    </div>
  {/if}

  <!-- Batch annotation modal -->

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
    visibility: visible;
  }

  table.loading {
    visibility: hidden;
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

  .annotate-button,
  .clear-button {
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

  .annotate-button:hover,
  .clear-button:hover {
    opacity: 0.8;
  }

  .annotate-button:focus,
  .clear-button:focus {
    outline: none;
    box-shadow: 0 0 0 2px #4a90e2;
  }
</style>
