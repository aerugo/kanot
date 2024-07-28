<script lang="ts">
	import { codes } from '../stores/codeStore';
	import type { Code } from "../types";

	interface Option {
		id: number;
		name: string;
	}

	interface Filter {
		id: number;
		name: string;
		type: 'series' | 'segment' | 'code' | 'type';
	}

	export let selectedSeries: number[] = [];
	export let selectedSegments: number[] = [];
	export let selectedCodes: number[] = [];
	export let seriesOptions: Option[] = [];
	export let segmentOptions: Option[] = [];
	export let onClearFilter: (id: number, type: 'series' | 'segment' | 'code' | 'type') => void;
	export let onClearAll: () => void;

	function isFilter(item: Filter | null): item is Filter {
		return item !== null;
	}

	$: selectedSeriesNames = selectedSeries
		.map((id) => {
			const series = seriesOptions.find((s) => s.id === id);
			return series ? { id: series.id, name: series.name, type: 'series' as const } : null;
		})
		.filter(isFilter);

	$: selectedSegmentNames = selectedSegments
		.map((id) => {
			const segment = segmentOptions.find((s) => s.id === id);
			return segment ? { id: segment.id, name: segment.name, type: 'segment' as const } : null;
		})
		.filter(isFilter);

	$: selectedCodeNames = selectedCodes
		.map((codeId) => {
			const code = $codes.find((c: Code) => c.code_id === codeId);
			return code ? { id: code.code_id, name: code.term, type: 'code' as const } : null;
		})
		.filter(isFilter);

	$: selectedTypeNames = selectedTypes
		.map((typeId) => {
			const codeType = $codeTypes.find((ct) => ct.type_id === typeId);
			return codeType ? { id: codeType.type_id, name: codeType.type_name, type: 'type' as const } : null;
		})
		.filter(isFilter);

	$: allSelectedFilters = [...selectedSeriesNames, ...selectedSegmentNames, ...selectedCodeNames, ...selectedTypeNames];

	function getFilterColor(type: Filter['type']): string {
		switch (type) {
			case 'series':
				return 'orange';
			case 'segment':
				return 'green';
			case 'code':
				return 'blue';
			default:
				return 'gray';
		}
	}
</script>

<div class="selected-filters">
	{#each allSelectedFilters as filter}
		{#if filter !== null}
			<span class="filter-tag" style="background-color: {getFilterColor(filter.type)}">
				{filter.name}
				<button on:click={() => onClearFilter(filter.id, filter.type)}>×</button>
			</span>
		{/if}
	{/each}
	{#if allSelectedFilters.length > 1}
		<button class="clear-all-filters" on:click={onClearAll}>Clear All</button>
	{/if}
</div>

<style>
	.selected-filters {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}

	.filter-tag {
		border-radius: 16px;
		padding: 0.25rem 0.5rem;
		display: flex;
		align-items: center;
		font-size: 0.9rem;
		color: white;
	}

	.filter-tag button {
		background: none;
		border: none;
		color: white;
		font-size: 1rem;
		cursor: pointer;
		padding: 0 0.25rem;
		margin-left: 0.25rem;
	}

	.clear-all-filters {
		background-color: #f0f0f0;
		border: none;
		border-radius: 16px;
		padding: 0.25rem 0.5rem;
		cursor: pointer;
		font-size: 0.9rem;
	}
</style>
