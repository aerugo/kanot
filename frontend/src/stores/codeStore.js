import { writable } from 'svelte/store';
import { fetchCodes, fetchCodeTypes } from '../utils/api.js';

function createCodeStore() {
    const { subscribe, set, update } = writable([]);

    return {
        subscribe,
        set,
        update,
        refresh: async () => {
            try {
                const codes = await fetchCodes();
                set(codes);
            } catch (error) {
                console.error('Error fetching codes:', error);
            }
        },
        add: (newCode) => update(codes => [...codes, newCode]),
        remove: (id) => update(codes => codes.filter(code => code.code_id !== id)),
        edit: (updatedCode) => update(codes => 
            codes.map(code => code.code_id === updatedCode.code_id ? updatedCode : code)
        )
    };
}

function createCodeTypeStore() {
    const { subscribe, set } = writable([]);

    return {
        subscribe,
        refresh: async () => {
            try {
                const types = await fetchCodeTypes();
                set(types);
            } catch (error) {
                console.error('Error fetching code types:', error);
            }
        }
    };
}

export const codes = createCodeStore();
export const codeTypes = createCodeTypeStore();