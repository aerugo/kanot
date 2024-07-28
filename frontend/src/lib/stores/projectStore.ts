import { writable } from 'svelte/store';

export const currentProject = writable<number>(1);
