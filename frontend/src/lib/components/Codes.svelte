<script lang="ts">
	import { onMount } from 'svelte';
	import { codes, codeTypes } from '../stores/codeStore';
	import { currentProject } from '../stores/projectStore';
	import type { Code } from "../types";
	import AddCodeForm from './AddCodeForm.svelte';
	import CodeList from './CodeList.svelte';
	import EditCodeModal from './EditCodeModal.svelte';
	import FilterDropdown from './FilterDropdown.svelte';
	import SearchBar from './SearchBar.svelte';
	import SelectedFilters from './SelectedFilters.svelte';

	interface Option {
		id: number;
		name: string;
	}

	let filteredCodes: Code[] = [];
	let selectedTypes: number[] = [];
	let selectedCodes: number[] = [];
	let seriesOptions: Option[] = [];
	let segmentOptions: Option[] = [];
	let isFilterOpen: boolean = false;
	let searchTerm: string = '';
	let editingCode: Code | null = null;

	onMount((): void => {
		if ($currentProject !== null) {
			codes.refresh($currentProject);
			codeTypes.refresh($currentProject);
		}
		// Initialize seriesOptions and segmentOptions here if needed
	});

	$: if ($currentProject !== null) {
		codes.refresh($currentProject);
		codeTypes.refresh($currentProject);
	}

	$: {
		filteredCodes = $codes.filter(
			(code: Code) =>
				(selectedTypes.length === 0 ||
					(code.code_type && selectedTypes.includes(code.code_type.type_id))) &&
				(searchTerm === '' ||
					code.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
					(code.description && code.description.toLowerCase().includes(searchTerm.toLowerCase())))
		);
	}

	function handleSearch(event: CustomEvent<string>): void {
		searchTerm = event.detail;
	}

	function handleTypesChanged(event: CustomEvent<number[]>): void {
		selectedTypes = event.detail;
	}

	function handleCodeAdded(event: Event): void {
		codes.refresh($currentProject);
	}

	function handleEditCode(event: CustomEvent<Code>): void {
		editingCode = event.detail;
		console.log('Editing code:', editingCode); // Add this line for debugging
	}

	function handleCodeUpdated(event: CustomEvent<Code>): void {
		codes.edit(event.detail);
		editingCode = null;
	}

	function handleDeleteCode(event: CustomEvent<number>): void {
		codes.remove(event.detail);
	}

	function clearFilter(id: number, type: 'series' | 'segment' | 'code' | 'type'): void {
		if (type === 'code') {
			selectedCodes = selectedCodes.filter((codeId) => codeId !== id);
		} else if (type === 'series') {
			// Implement series filter clearing if needed
		} else if (type === 'segment') {
			// Implement segment filter clearing if needed
		} else if (type === 'type') {
			selectedTypes = selectedTypes.filter((typeId) => typeId !== id);
		}
	}

	function handleClearFilter(id: number, type: 'series' | 'segment' | 'code' | 'type'): void {
		clearFilter(id, type);
	}

	function clearAllFilters(): void {
		selectedTypes = [];
		selectedCodes = [];
		// Clear series and segments filters if needed
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
				options={$codeTypes.map((type) => ({ id: type.type_id, name: type.type_name }))}
				selected={selectedTypes}
				on:change={handleTypesChanged}
			/>
		</div>

		<SelectedFilters
			selectedSeries={[]}
			selectedSegments={[]}
			{selectedCodes}
			{seriesOptions}
			{segmentOptions}
			onClearFilter={handleClearFilter}
			onClearAll={clearAllFilters}
		/>

		<CodeList 
			{filteredCodes} 
			on:editCode={handleEditCode} 
			on:deleteCode={handleDeleteCode}
			on:codeUpdated={() => codes.refresh($currentProject)}
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
