import { derived, writable } from 'svelte/store';
import { searchElements } from '../api';
import type { Element } from '../types';

export interface Series {
	series_id: number;
	series_title: string;
}

export interface Series {
	segment_id: number;
	segment_title: string;
}

// Store to hold all elements
export const allElements = writable<Element[]>([]);

// Store for search term
export const searchTerm = writable<string>('');

// Stores for selected filters
export const selectedSeries = writable<number[]>([]);
export const selectedSegments = writable<number[]>([]);
export const selectedCodes = writable<number[]>([]);

// Derived store for filtered elements based on search term and selected filters
export const filteredElements = derived(
	[allElements, searchTerm, selectedSeries, selectedSegments, selectedCodes],
	([$allElements, $searchTerm, $selectedSeries, $selectedSegments, $selectedCodes]: [
		Element[],
		string,
		number[],
		number[],
		number[]
	]) =>
		$allElements.filter(
			(element) =>
				($searchTerm === '' ||
					element.element_text.toLowerCase().includes($searchTerm.toLowerCase())) &&
				($selectedSeries.length === 0 ||
					$selectedSeries.includes(element.segment?.series?.series_id ?? -1)) &&
				($selectedSegments.length === 0 ||
					$selectedSegments.includes(element.segment?.segment_id ?? -1)) &&
				($selectedCodes.length === 0 ||
					element.annotations.some((a) => $selectedCodes.includes(a.code?.code_id ?? -1)))
		)
);

/**
 * Load more elements with pagination
 * @param page - Page number
 * @param searchTerm - Search term
 * @param selectedSeries - Selected series IDs
 * @param selectedSegments - Selected segment IDs
 * @param selectedCodes - Selected code IDs
 * @param pageSize - Number of elements per page
 * @returns Promise<Element[]> - List of new elements
 */
export async function loadMoreElements(
	projectId: number,
	page: number = 1,
	searchTerm: string = '',
	selectedSeries: number[] = [],
	selectedSegments: number[] = [],
	selectedCodes: number[] = [],
	pageSize: number = 100
): Promise<Element[]> {
	try {
		const newElements = await searchElements(
			projectId,
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
				const combinedElements = [...elements, ...newElements];
				const uniqueElementIds = new Set();
				const uniqueElements = combinedElements.filter((element) => {
					if (uniqueElementIds.has(element.element_id)) {
						console.warn('Duplicate element ID found:', element.element_id);
						return false;
					}
					uniqueElementIds.add(element.element_id);
					return true;
				});
				return uniqueElements;
			}
		});

		return newElements;
	} catch (error) {
		console.error('Error loading more elements:', error);
		throw error;
	}
}
