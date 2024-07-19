import { fetchCodes, fetchCodeTypes } from '$lib/api';

export async function load({ fetch }) {
  try {
    const [codesData, codeTypesData] = await Promise.all([
      fetchCodes(fetch),
      fetchCodeTypes(fetch)
    ]);
    
    return {
      codes: codesData,
      codeTypes: codeTypesData
    };
  } catch (error) {
    console.error('Error loading initial data:', error);
    return {
      codes: [],
      codeTypes: []
    };
  }
}