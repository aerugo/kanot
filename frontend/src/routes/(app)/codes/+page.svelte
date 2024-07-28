<script>
  import Codes from '$lib/components/Codes.svelte';
  import { codes, codeTypes } from '$lib/stores/codeStore.ts';
  import { currentProject } from '$lib/stores/projectStore';
  import { onMount } from 'svelte';

  export let data;

  onMount(() => {
    codes.set(data.codes);
    codeTypes.set(data.codeTypes);
  });

  $: if ($currentProject) {
    codes.refresh($currentProject, fetch);
    codeTypes.refresh(fetch);
  }
</script>

<Codes currentProjectId={$currentProject} />
