const BASE_URL = 'http://localhost:8000';

/**
 * Type for FetchFunction
 */
type FetchFunction = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

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
 * @param {FetchFunction} [fetchFunc=fetch] - The fetch function
 * @returns {Promise<any>}
 */
export async function fetchCodes(projectId: number, fetchFunc: FetchFunction = fetch): Promise<any> {
	return apiRequest(`/codes/?project_id=${projectId}`, 'GET', null, fetchFunc);
}

export async function fetchProjects(fetchFunc: FetchFunction = fetch): Promise<any> {
	return apiRequest('/projects/', 'GET', null, fetchFunc);
}

/**
 * Fetch code types
 *
 * @param {number} projectId - The project ID
 * @param {FetchFunction} [fetchFunc=fetch] - The fetch function
 * @returns {Promise<any>}
 */
export async function fetchCodeTypes(projectId: number, fetchFunc: FetchFunction = fetch): Promise<any> {
	return apiRequest(`/code_types/?project_id=${projectId}`, 'GET', null, fetchFunc);
}

/**
 * Fetch paginated elements
 *
 * @param {number} projectId - The project ID
 * @param {number} [page=1] - The page number
 * @param {number} [pageSize=100] - The page size
 * @returns {Promise<any>}
 */
export async function fetchPaginatedElements(
	projectId: number,
	page: number = 1,
	pageSize: number = 100
): Promise<any> {
	return apiRequest(`/elements/?project_id=${projectId}&skip=${(page - 1) * pageSize}&limit=${pageSize}`);
}

/**
 * Search elements
 *
 * @param {number} projectId - The project ID
 * @param {string} searchTerm - The search term
 * @param {number[]} [seriesIds=[]] - Array of series IDs
 * @param {number[]} [segmentIds=[]] - Array of segment IDs
 * @param {number[]} [codeIds=[]] - Array of code IDs
 * @param {number} [page=1] - The page number
 * @param {number} [pageSize=100] - The page size
 * @returns {Promise<any>}
 */
export async function searchElements(
	projectId: number,
	searchTerm: string,
	seriesIds: number[] = [],
	segmentIds: number[] = [],
	codeIds: number[] = [],
	page: number = 1,
	pageSize: number = 100
): Promise<any> {
	const params = new URLSearchParams({
		project_id: projectId.toString(),
		search_term: searchTerm,
		skip: ((page - 1) * pageSize).toString(),
		limit: pageSize.toString()
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
 * @returns {Promise<any>}
 */
export async function createBatchAnnotations(
	elementIds: number[],
	codeIds: number[]
): Promise<any> {
	return apiRequest('/batch_annotations/', 'POST', { element_ids: elementIds, code_ids: codeIds });
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
): Promise<any> {
	return apiRequest('/batch_annotations/', 'DELETE', {
		element_ids: elementIds,
		code_ids: codeIds
	});
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
export async function fetchSeries(projectId: number): Promise<any> {
	return apiRequest(`/series/?project_id=${projectId}`);
}

// Segments API

/**
 * Fetch segments
 *
 * @param {number} projectId - The project ID
 * @returns {Promise<any>}
 */
export async function fetchSegments(projectId: number): Promise<any> {
	return apiRequest(`/segments/?project_id=${projectId}`);
}
