import { browser } from '$app/environment';
import { fetchCodes, fetchCodeTypes } from '$lib/api';
import { writable, type Writable } from 'svelte/store';
import type { Code, CodeType } from '../types';

// Define a type for the fetch function
type FetchFunction = typeof fetch;

function createCodeStore() {
  const { subscribe, set, update }: Writable<Code[]> = writable([]);

  return {
    subscribe,
    set,
    update,
    refresh: async (projectId: number | null, fetchFunc: FetchFunction = fetch) => {
      if (browser && projectId !== null) {
        try {
          const codes = await fetchCodes(projectId, fetchFunc);
          set(codes);
        } catch (error) {
          console.error('Error fetching codes:', error);
        }
      }
    },
    add: (newCode: Code) => update(codes => [...codes, newCode]),
    remove: (id: number) => update(codes => codes.filter(code => code.code_id !== id)),
    edit: (updatedCode: Code) => update(codes => 
      codes.map(code => code.code_id === updatedCode.code_id ? updatedCode : code)
    )
  };
}

function createCodeTypeStore() {
  const { subscribe, set }: Writable<CodeType[]> = writable([]);

  return {
    subscribe,
    set,
    refresh: async (projectId: number | null, fetchFunc: FetchFunction = fetch) => {
      if (browser && projectId !== null) {
        try {
          const types = await fetchCodeTypes(projectId, fetchFunc);
          console.log('Fetched code types:', types);
          set(types);
        } catch (error) {
          console.error('Error fetching code types:', error);
        }
      }
    }
  };
}

export const codes = createCodeStore();
export const codeTypes = createCodeTypeStore();
