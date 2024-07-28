<script lang="ts">
  import Content from '$lib/components/Content.svelte';
  import { currentProject } from '$lib/stores/projectStore';
</script>

{#if $currentProject !== null}
  <Content />
{:else}
  <p>Please select a project.</p>
{/if}
