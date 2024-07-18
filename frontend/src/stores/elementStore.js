import { derived, writable } from "svelte/store";
import { searchElements } from "../utils/api.js";

// Store to hold all elements
export const allElements = writable([]);

// Store for search term
export const searchTerm = writable("");

// Stores for selected filters
export const selectedSeries = writable([]);
export const selectedSegments = writable([]);
export const selectedCodes = writable([]);

// Derived store for filtered elements based on search term and selected filters
export const filteredElements = derived(
  [allElements, searchTerm, selectedSeries, selectedSegments, selectedCodes],
  ([
    $allElements,
    $searchTerm,
    $selectedSeries,
    $selectedSegments,
    $selectedCodes,
  ]) =>
    $allElements.filter(
      (element) =>
        ($searchTerm === "" ||
          element.element_text
            .toLowerCase()
            .includes($searchTerm.toLowerCase())) &&
        ($selectedSeries.length === 0 ||
          $selectedSeries.includes(element.segment?.series?.series_id)) &&
        ($selectedSegments.length === 0 ||
          $selectedSegments.includes(element.segment?.segment_id)) &&
        ($selectedCodes.length === 0 ||
          element.annotations.some((a) =>
            $selectedCodes.includes(a.code?.code_id)
          ))
    )
);

/**
 * Load more elements with pagination
 * @param {number} page - Page number
 * @param {string} searchTerm - Search term
 * @param {Array} selectedSeries - Selected series IDs
 * @param {Array} selectedSegments - Selected segment IDs
 * @param {Array} selectedCodes - Selected code IDs
 * @param {number} pageSize - Number of elements per page
 * @returns {Promise<Array>} - List of new elements
 */
export async function loadMoreElements(
  page = 1,
  searchTerm = "",
  selectedSeries = [],
  selectedSegments = [],
  selectedCodes = [],
  pageSize = 100
) {
  try {
    const newElements = await searchElements(
      searchTerm,
      selectedSeries,
      selectedSegments,
      selectedCodes,
      page,
      pageSize
    );

    allElements.update((elements) => {
      if (page === 1) {
        return newElements;
      } else {
        return [...elements, ...newElements];
      }
    });

    return newElements;
  } catch (error) {
    console.error("Error loading more elements:", error);
    throw error;
  }
}
