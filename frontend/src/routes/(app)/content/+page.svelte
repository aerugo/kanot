<script lang="ts">
  import Content from '$lib/components/Content.svelte';
  import { currentProject } from '$lib/stores/projectStore';
  import { onMount } from 'svelte';

  let projectId: number | null = null;

  onMount(() => {
    const unsubscribe = currentProject.subscribe(value => {
      projectId = value;
      console.log('Current Project ID in content page:', projectId);
    });

    return unsubscribe;
  });
</script>

{#if projectId !== null}
  <Content currentProjectId={projectId} />
{:else}
  <p>Please select a project.</p>
{/if}
