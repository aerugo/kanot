import { currentProject } from '$lib/stores/projectStore';
import { get } from 'svelte/store';
import type { Code, CodeType, Project } from './types';

const BASE_URL = 'http://localhost:8000';

/**
 * Type for FetchFunction
 */
type FetchFunction = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

/**
 * Get the current project ID
 *
 * @returns {number} The current project ID
 */
function getCurrentProjectId(): number {
    const projectId = get(currentProject);
    if (projectId === undefined || projectId === null) {
        return 0; // Return a default project ID
    }
    return projectId;
}

/**
 * General function for API requests
 *
 * @param {string} endpoint - The API endpoint
 * @param {string} [method='GET'] - The HTTP method
 * @param {Object|null} [data=null] - The request payload
 * @param {FetchFunction} [fetchFunc=fetch] - The fetch function
 * @returns {Promise<any>} - The API response data
 */
async function apiRequest(
	endpoint: string,
	method: string = 'GET',
	data: any = null,
	fetchFunc: FetchFunction = fetch
): Promise<any> {
	const url = `${BASE_URL}${endpoint}`;
	const options: RequestInit = {
		method,
		headers: {
			'Content-Type': 'application/json'
		}
	};

	if (data) {
		options.body = JSON.stringify(data);
	}

	const response = await fetchFunc(url, options);

	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		throw new Error(errorData.message || response.statusText);
	}

	return response.json();
}

/**
 * Fetch codes
 *
 * @param {number} projectId - The project ID
 * @param {FetchFunction} [fetchFunc=fetch] - The fetch function
 * @returns {Promise<any>}
 */
export async function fetchCodes(): Promise<Code[]> {
	return apiRequest(`/codes/?project_id=${getCurrentProjectId()}`);
}

export async function fetchProjects(): Promise<Project[]> {
	return apiRequest('/projects/');
}

/**
 * Fetch code types
 *
 * @returns {Promise<CodeType[]>}
 */
export async function fetchCodeTypes(): Promise<CodeType[]> {
	return apiRequest(`/code_types/?project_id=${getCurrentProjectId()}`);
}

/**
 * Fetch paginated elements
 *
 * @param {number} [page=1] - The page number
 * @param {number} [pageSize=100] - The page size
 * @returns {Promise<any>}
 */
export async function fetchPaginatedElements(
	page: number = 1,
	pageSize: number = 100
): Promise<any> {
	const projectId = getCurrentProjectId();
	if (projectId === undefined || projectId === null) {
		console.error('Project ID is undefined or null in fetchPaginatedElements');
		throw new Error("Project ID is required");
	}
	return apiRequest(`/elements/?project_id=${projectId}&skip=${(page - 1) * pageSize}&limit=${pageSize}`);
}

/**
 * Search elements
 *
 * @param {string} searchTerm - The search term
 * @param {number[]} [seriesIds=[]] - Array of series IDs
 * @param {number[]} [segmentIds=[]] - Array of segment IDs
 * @param {number[]} [codeIds=[]] - Array of code IDs
 * @param {number} [page=1] - The page number
 * @param {number} [pageSize=100] - The page size
 * @returns {Promise<any>}
 */
export async function searchElements(
	searchTerm: string,
	seriesIds: number[] = [],
	segmentIds: number[] = [],
	codeIds: number[] = [],
	page: number = 1,
	pageSize: number = 100
): Promise<any> {
	const params = new URLSearchParams({
		project_id: getCurrentProjectId().toString(),
		search_term: searchTerm,
		skip: Math.max(0, (page - 1) * pageSize).toString(),
		limit: Math.max(1, pageSize).toString()
	});

	if (seriesIds.length) params.append('series_ids', seriesIds.join(','));
	if (segmentIds.length) params.append('segment_ids', segmentIds.join(','));
	if (codeIds.length) params.append('code_ids', codeIds.join(','));

	return apiRequest(`/search_elements/?${params}`);
}

/**
 * Add a new code
 *
 * @param {Object} newCode - The new code data
 * @returns {Promise<any>}
 */
export async function addCode(newCode: any): Promise<any> {
	return apiRequest('/codes/', 'POST', newCode);
}

/**
 * Update an existing code
 *
 * @param {number|string} id - The code ID
 * @param {Object} updatedCode - The updated code data
 * @returns {Promise<any>}
 */
export async function updateCode(id: number | string, updatedCode: any): Promise<any> {
	return apiRequest(`/codes/${id}`, 'PUT', updatedCode);
}

/**
 * Delete a code
 *
 * @param {number|string} id - The code ID
 * @returns {Promise<any>}
 */
export async function deleteCode(id: number | string): Promise<any> {
	return apiRequest(`/codes/${id}`, 'DELETE');
}

// Annotations API

/**
 * Create an annotation
 *
 * @param {Object} annotationData - The annotation data
 * @returns {Promise<any>}
 */
export async function createAnnotation(annotationData: any): Promise<any> {
	return apiRequest('/annotations/', 'POST', annotationData);
}

/**
 * Create batch annotations
 *
 * @param {number[]} elementIds - Array of element IDs
 * @param {number[]} codeIds - Array of code IDs
 * @param {number} projectId - The project ID
 * @returns {Promise<any>}
 */
export async function createBatchAnnotations(
	elementIds: number[],
	codeIds: number[],
	projectId: number
): Promise<any> {
	return apiRequest('/batch_annotations/', 'POST', { element_ids: elementIds, code_ids: codeIds, project_id: projectId });
}

/**
 *
 * @param {number[]} elementIds - Array of element IDs
 * @param {number[]} codeIds - Array of code IDs
 * @returns {Promise<any>}
 */
export async function removeBatchAnnotations(
	elementIds: number[],
	codeIds: number[]
): Promise<{ success: boolean; message: string; removedCount: number }> {
	try {
		console.log('removeBatchAnnotations called with:', { elementIds, codeIds });
		const response = await fetch(`${BASE_URL}/batch_annotations/?${new URLSearchParams({
			element_ids: elementIds.join(','),
			code_ids: codeIds.join(',')
		})}`, {
			method: 'DELETE',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		console.log('API response status:', response.status);
		const responseData = await response.json();
		console.log('API response data:', responseData);

		if (!response.ok) {
			console.error('Error response:', responseData);
			return { success: false, message: responseData.detail || 'Failed to remove annotations', removedCount: 0 };
		}

		return { success: true, message: responseData.message, removedCount: responseData.removed_count };
	} catch (error) {
		console.error('Error in removeBatchAnnotations:', error);
		return { success: false, message: `An error occurred while removing annotations: ${error.message}`, removedCount: 0 };
	}
}

/**
 * Delete an annotation
 *
 * @param {number|string} annotationId - The annotation ID
 * @returns {Promise<any>}
 */
export async function deleteAnnotation(annotationId: number | string): Promise<any> {
	return apiRequest(`/annotations/${annotationId}`, 'DELETE');
}

// Elements API

// These functions have been moved up in the file, so we're removing the duplicates here.

// Series API

/**
 * Fetch series
 *
 * @returns {Promise<any>}
 */
export async function fetchSeries(): Promise<any> {
	return apiRequest(`/series/?project_id=${getCurrentProjectId()}`);
}

// Segments API

/**
 * Fetch segments
 *
 * @returns {Promise<any>}
 */
export async function fetchSegments(): Promise<any> {
	return apiRequest(`/segments/?project_id=${getCurrentProjectId()}`);
}
