<script>
  import Codes from '$lib/components/Codes.svelte';
  import { codes, codeTypes } from '$lib/stores/codeStore.ts';
  import { onMount } from 'svelte';

  export let data;

  onMount(() => {
    codes.set(data.codes);
    codeTypes.set(data.codeTypes);
    codes.refresh(fetch);
    codeTypes.refresh(fetch);
  });
</script>

<Codes />