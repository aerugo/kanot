<script lang="ts">
    import { onMount } from 'svelte';
    import { fetchProjects } from '../api';
    import type { Project } from '../types';
    import { currentProject } from '../stores/projectStore';

    let projects: Project[] = [];

    onMount(async () => {
        projects = await fetchProjects();
        if (projects.length > 0) {
            currentProject.set(projects[0].project_id);
        }
    });

    function handleProjectChange(event: Event) {
        const target = event.target as HTMLSelectElement;
        const selectedProjectId = parseInt(target.value, 10);
        currentProject.set(selectedProjectId);
    }
</script>

<div class="project-switcher">
    <select on:change={handleProjectChange} value={$currentProject}>
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
