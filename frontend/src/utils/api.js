// api.js
import axios from "axios";

const BASE_URL = "http://localhost:8000";

// Codes API

export async function fetchCodes() {
  try {
    const response = await axios.get(`${BASE_URL}/codes/`);
    return response.data;
  } catch (error) {
    console.error("Error fetching codes:", error);
    throw error;
  }
}

export async function fetchCodeTypes() {
  try {
    const response = await axios.get(`${BASE_URL}/code_types/`);
    return response.data;
  } catch (error) {
    console.error("Error fetching code types:", error);
    throw error;
  }
}

export async function addCode(newCode) {
  try {
    const response = await axios.post(`${BASE_URL}/codes/`, newCode);
    return response.data;
  } catch (error) {
    console.error("Error adding code:", error);
    throw error;
  }
}

export async function updateCode(id, updatedCode) {
  try {
    const response = await axios.put(`${BASE_URL}/codes/${id}`, updatedCode);
    return response.data;
  } catch (error) {
    console.error("Error updating code:", error);
    throw error;
  }
}

export async function deleteCode(id) {
  try {
    await axios.delete(`${BASE_URL}/codes/${id}`);
  } catch (error) {
    console.error("Error deleting code:", error);
    throw error;
  }
}

// Annotations API

export async function createAnnotation(annotationData) {
  try {
    const response = await axios.post(`${BASE_URL}/annotations/`, annotationData);
    return response.data;
  } catch (error) {
    console.error("Error creating annotation:", error);
    throw error;
  }
}


export async function createBatchAnnotations(elementIds, codeIds) {
  try {
    const response = await axios.post(`${BASE_URL}/batch_annotations/`, { element_ids: elementIds, code_ids: codeIds });
    return response.data; // This should be an array of new annotations
  } catch (error) {
    console.error("Error creating batch annotations:", error);
    throw error;
  }
}

export async function deleteAnnotation(annotationId) {
  try {
    await axios.delete(`${BASE_URL}/annotations/${annotationId}`);
  } catch (error) {
    console.error("Error deleting annotation:", error);
    throw error;
  }
}

// Elements API

export async function fetchPaginatedElements(page = 1, pageSize = 100) {
  try {
    const response = await axios.get(`${BASE_URL}/elements/`, {
      params: { skip: (page - 1) * pageSize, limit: pageSize },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching paginated elements:", error);
    throw error;
  }
}

export async function searchElements(
  searchTerm,
  seriesIds = [],
  segmentIds = [],
  codeIds = [],
  page = 1,
  pageSize = 100
) {
  const params = new URLSearchParams({
    search_term: searchTerm,
    skip: ((page - 1) * pageSize).toString(),
    limit: pageSize.toString(),
  });
  
  if (seriesIds.length) params.append("series_ids", seriesIds.join(","));
  if (segmentIds.length) params.append("segment_ids", segmentIds.join(","));
  if (codeIds.length) params.append("code_ids", codeIds.join(","));
  
  try {
    const response = await axios.get(`${BASE_URL}/search_elements/?${params}`);
    return response.data;
  } catch (error) {
    console.error("Failed to search elements:", error);
    throw error;
  }
}

// Series API

export async function fetchSeries() {
  const response = await fetch(`${BASE_URL}/series/`);
  if (!response.ok) throw new Error("Failed to fetch series");
  return response.json();
}

// Segments API

export async function fetchSegments() {
  const response = await fetch(`${BASE_URL}/segments/`);
  if (!response.ok) throw new Error("Failed to fetch segments");
  return response.json();
}
