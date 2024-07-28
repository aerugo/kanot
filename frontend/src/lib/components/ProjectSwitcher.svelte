<script lang="ts">
    import { onMount } from 'svelte';
    import { fetchProjects } from '../api';
    import type { Project } from '../types';

    let projects: Project[] = [];
    let selectedProjectId: number | null = null;

    onMount(async () => {
        projects = await fetchProjects();
        if (projects.length > 0) {
            selectedProjectId = projects[0].project_id;
            dispatch('projectSelected', selectedProjectId);
        }
    });

    function handleProjectChange(event: Event) {
        const target = event.target as HTMLSelectElement;
        selectedProjectId = parseInt(target.value, 10);
        dispatch('projectSelected', selectedProjectId);
    }

    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher<{
        projectSelected: number;
    }>();
</script>

<div class="project-switcher">
    <select on:change={handleProjectChange} value={selectedProjectId}>
        {#each projects as project}
            <option value={project.project_id}>{project.project_title}</option>
        {/each}
    </select>
</div>

<style>
    .project-switcher {
        margin-right: 1rem;
    }

    select {
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #ccc;
        background-color: white;
        font-size: 1rem;
    }
</style>
