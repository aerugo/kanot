import { currentProject } from '$lib/stores/projectStore';

export function load() {
    currentProject.set(0);
}
