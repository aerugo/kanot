<script>
  import Codes from '$lib/components/Codes.svelte';
  import { codes, codeTypes } from '$lib/stores/codeStore.ts';
  import { onMount } from 'svelte';

  export let data;

  console.log('Page data:', data);

  onMount(() => {
    console.log('Setting codes:', data.codes);
    console.log('Setting code types:', data.codeTypes);
    codes.set(data.codes);
    codeTypes.set(data.codeTypes);
    codes.refresh(fetch);
    codeTypes.refresh(fetch);
  });
</script>

<Codes />