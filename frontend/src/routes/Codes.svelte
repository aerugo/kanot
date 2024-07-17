<script>
  import { onMount } from "svelte";
  import AddCodeForm from "../components/AddCodeForm.svelte";
  import CodeList from "../components/CodeList.svelte";
  import EditCodeModal from "../components/EditCodeModal.svelte";
  import FilterDropdown from "../components/FilterDropdown.svelte";
  import SearchBar from "../components/SearchBar.svelte";
  import SelectedFilters from "../components/SelectedFilters.svelte";
  import { codes, codeTypes } from "../stores/codeStore.js";

  let filteredCodes = [];
  let selectedTypes = [];
  let isFilterOpen = false;
  let searchTerm = "";
  let editingCode = null;

  onMount(() => {
    codes.refresh();
    codeTypes.refresh();
  });

  $: {
    filteredCodes = $codes.filter(
      (code) =>
        (selectedTypes.length === 0 ||
          selectedTypes.includes(code.code_type?.type_id)) &&
        (searchTerm === "" ||
          code.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
          code.description.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }

  function handleSearch(event) {
    searchTerm = event.detail;
  }

  function handleTypesChanged(event) {
    selectedTypes = event.detail;
  }

  function handleCodeAdded(event) {
    codes.refresh();
  }

  function handleEditCode(event) {
    editingCode = event.detail;
  }

  function handleCodeUpdated(event) {
    codes.edit(event.detail);
    editingCode = null;
  }

  function handleDeleteCode(id) {
    codes.remove(id);
  }

  function clearFilter(typeId) {
    selectedTypes = selectedTypes.filter(id => id !== typeId);
  }

  function clearAllFilters() {
    selectedTypes = [];
  }
</script>

<main>
  <h1>Kanot Code Management</h1>

  <AddCodeForm on:codeAdded={handleCodeAdded} />

  <section class="codes-list">
    <h2>Codes List</h2>

    <div class="filters">
      <SearchBar on:search={handleSearch} placeholder="Search codes..." debounceDelay={300} />
      <FilterDropdown
        label="Filter by Type"
        options={$codeTypes.map(type => ({ id: type.type_id, name: type.type_name }))}
        bind:selected={selectedTypes}
        bind:isOpen={isFilterOpen}
        on:change={handleTypesChanged}
      />
    </div>

    <SelectedFilters
      selectedTypes={selectedTypes}
      onClearFilter={clearFilter}
      onClearAll={clearAllFilters}
    />

    <CodeList
      {filteredCodes}
      on:editCode={handleEditCode}
      on:deleteCode={handleDeleteCode}
    />
  </section>

  {#if editingCode}
    <EditCodeModal
      code={editingCode}
      on:codeUpdated={handleCodeUpdated}
      on:close={() => (editingCode = null)}
    />
  {/if}
</main>

<style>
  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  h1 {
    font-size: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
    color: #2c3e50;
  }

  h2 {
    font-size: 1.8rem;
    margin-bottom: 1rem;
    color: #2c3e50;
  }

  .codes-list {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 2rem;
    margin-bottom: 2rem;
  }

  .filters {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
</style>
