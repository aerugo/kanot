<script lang="ts">
  import Content from '$lib/components/Content.svelte';
  import { currentProject } from '$lib/stores/projectStore';
</script>

<Content currentProjectId={$currentProject} />
