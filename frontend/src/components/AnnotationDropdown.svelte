<script>
    import { createEventDispatcher } from 'svelte';
    import { codes } from '../stores/codeStore.js';
    import { clickOutside } from '../utils/clickOutside.js';
  
    export let isOpen = false;
    export let elementId;
  
    const dispatch = createEventDispatcher();
  
    let searchTerm = '';
    let selectedIndex = 0;
  
    $: filteredCodes = $codes.filter(code =>
      code.term.toLowerCase().includes(searchTerm.toLowerCase())
    );
  
    function selectCode(code) {
      dispatch('select', { elementId, codeId: code.code_id });
      close();
    }
  
    function handleKeydown(event) {
      if (event.key === 'ArrowDown') {
        selectedIndex = (selectedIndex + 1) % filteredCodes.length;
      } else if (event.key === 'ArrowUp') {
        selectedIndex = (selectedIndex - 1 + filteredCodes.length) % filteredCodes.length;
      } else if (event.key === 'Enter') {
        if (filteredCodes[selectedIndex]) {
          selectCode(filteredCodes[selectedIndex]);
        }
      } else if (event.key === 'Escape') {
        close();
      }
    }
  
    function close() {
      isOpen = false;
      searchTerm = '';
      selectedIndex = 0;
    }
  </script>
  
  <div class="annotation-dropdown" use:clickOutside on:clickoutside={close}>
    <input
      type="text"
      bind:value={searchTerm}
      placeholder="Search codes..."
      on:keydown={handleKeydown}
      autofocus
    />
    <ul>
      {#each filteredCodes as code, index}
        <li
          class:selected={index === selectedIndex}
          on:click={() => selectCode(code)}
        >
          {code.term}
        </li>
      {/each}
    </ul>
  </div>
  
  <style>
    .annotation-dropdown {
      position: absolute;
      background-color: white;
      border: 1px solid #ccc;
      border-radius: 4px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      z-index: 1000;
      max-height: 300px;
      overflow-y: auto;
      width: 250px;
    }
  
    input {
      width: 100%;
      padding: 8px;
      border: none;
      border-bottom: 1px solid #ccc;
    }
  
    ul {
      list-style-type: none;
      padding: 0;
      margin: 0;
    }
  
    li {
      padding: 8px;
      cursor: pointer;
    }
  
    li:hover, li.selected {
      background-color: #f0f0f0;
    }
  </style>