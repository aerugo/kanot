<script lang="ts">
	import { browser } from '$app/environment';
	import { onDestroy, onMount } from 'svelte';
	import { writable, type Writable } from 'svelte/store';
	import { fade, slide } from 'svelte/transition';
	import { get } from 'svelte/store';
	import {
		createAnnotation,
		createBatchAnnotations,
		deleteAnnotation,
		fetchSegments,
		fetchSeries,
		removeBatchAnnotations,
		searchElements
	} from '../api';
	import AnnotationDropdown from '../components/AnnotationDropdown.svelte';
	import BatchAnnotationModal from '../components/BatchAnnotationModal.svelte';
	import BatchRemovalModal from '../components/BatchRemovalModal.svelte';
	import FilterDropdown from '../components/FilterDropdown.svelte';
	import SearchBar from '../components/SearchBar.svelte';
	import SelectedFilters from '../components/SelectedFilters.svelte';
	import { codes } from '../stores/codeStore';
	import {
		filteredElements,
		loadMoreElements,
		searchTerm,
		selectedCodes,
		selectedSegments,
		selectedSeries
	} from '../stores/elementStore';
	import type { Annotation, Element, Series } from '../types';
	import { debounce } from '../utils/helpers';

	import { currentProject } from '../stores/projectStore';

	interface Option {
		id: number;
		name: string;
	}

	let elementsStore: Writable<Element[]> = writable([]);
	let page: number = 1;
	let loading: boolean = false;
	let hasMore: boolean = true;
	let annotationDropdownOpen: { [key: number]: boolean } = {};
	let selectedElementIds: number[] = [];
	let showBatchAnnotationModal: boolean = false;
	let showBatchRemovalModal: boolean = false;
	let seriesOptions: Option[] = [];
	let segmentOptions: Option[] = [];
	let rangeStartIndex: number = -1;

	$: $elementsStore = $filteredElements;

	const debouncedSearch = debounce(async () => {
		if (
			$searchTerm.length >= 3 ||
			$selectedSeries.length > 0 ||
			$selectedSegments.length > 0 ||
			$selectedCodes.length > 0
		) {
			await resetSearch();
		}
	}, 300);

	import { codeTypes } from '../stores/codeStore';

	async function loadInitialData(): Promise<void> {
		if ($currentProject === null) {
			console.error('Current project is null');
			return;
		}
		console.log('Loading initial data for project:', $currentProject);
		await loadFilterOptions();
		await codes.refresh($currentProject);
		await codeTypes.refresh($currentProject);
		await resetSearch();
	}

	$: if ($currentProject !== null && $currentProject !== 0) {
		console.log('Current Project ID:', $currentProject);
		loadInitialData();
	}

	async function loadFilterOptions(): Promise<void> {
		if ($currentProject === null) {
			console.error('Current project ID is null');
			return;
		}
		try {
			const [series, segmentsData] = await Promise.all([
				fetchSeries(),
				fetchSegments()
			]);

			seriesOptions = (series as Series[]).map((s: Series) => ({
				id: s.series_id,
				name: s.series_title
			}));

			segmentOptions = (segmentsData as Series[]).map((s: Series) => ({
				id: s.segment_id,
				name: s.segment_title
			}));
		} catch (error) {
			console.error('Error loading filter options:', error);
		}
	}

	async function loadMoreData(): Promise<void> {
		if (!browser || loading || !hasMore) return;
		if ($currentProject === null || $currentProject === 0) {
			console.error('Invalid project in loadMoreData');
			return;
		}
		loading = true;
		console.log('Loading more data for project:', $currentProject);
		try {
			console.log('Fetching elements:', { 
				projectId: $currentProject, 
				searchTerm: $searchTerm, 
				page, 
				pageSize: 100 
			});
			const newElements = await searchElements(
				$searchTerm,
				$selectedSeries,
				$selectedSegments,
				$selectedCodes,
				page,
				100
			);
			elementsStore.update((currentElements) => {
				const updatedElements = page === 1 ? newElements : [...currentElements];
				// Filter out duplicates based on element_id
				const uniqueElements = newElements.filter(
					(newElement) =>
						!updatedElements.some(
							(existingElement) => existingElement.element_id === newElement.element_id
						)
				);
				return [...updatedElements, ...uniqueElements];
			});
			hasMore = newElements.length > 0;
			page++;
		} catch (error) {
			console.error('Error loading more elements:', error);
		} finally {
			loading = false;
		}
	}

	async function resetSearch(): Promise<void> {
		page = 1;
		elementsStore.set([]);
		hasMore = true;
		await loadMoreData();
	}

	const debouncedResetSearch = debounce(async () => {
		page = 1;
		elementsStore.set([]);
		hasMore = true;
		await loadMoreData();
	}, 300);

	const debouncedHandleScroll = debounce(() => {
		if (browser) {
			const bottom =
				window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 500;
			if (bottom && !loading && hasMore) {
				loadMoreData();
			}
		}
	}, 200);

	function handleInput(event: Event) {
		const target = event.target as HTMLInputElement;
		searchTerm.set(target.value);
	}

	function handleScroll(): void {
		debouncedHandleScroll();
	}

	onMount(async () => {
		if (browser) {
			window.addEventListener('scroll', handleScroll);
		}
	});

	onDestroy(() => {
		if (browser) {
			window.removeEventListener('scroll', handleScroll);
		}
	});

	$: if (
		$searchTerm.length >= 3 ||
		$selectedSeries.length > 0 ||
		$selectedSegments.length > 0 ||
		$selectedCodes.length > 0
	) {
		debouncedSearch();
	} else if (
		$searchTerm.length === 0 &&
		$selectedSeries.length === 0 &&
		$selectedSegments.length === 0 &&
		$selectedCodes.length === 0
	) {
		debouncedResetSearch();
	}

	function handleSearch(event: CustomEvent<string>): void {
		$searchTerm = event.detail;
		resetSearch();
	}

	function handleSeriesChanged(event: CustomEvent<number[]>): void {
		selectedSeries.set(event.detail);
		resetSearch();
	}

	function handleSegmentChanged(event: CustomEvent<number[]>): void {
		selectedSegments.set(event.detail);
		resetSearch();
	}

	function handleCodesChanged(event: CustomEvent<number[]>): void {
		selectedCodes.set(event.detail);
		resetSearch();
	}

	function clearFilter(id: number, type: 'series' | 'segment' | 'code' | 'type'): void {
		switch (type) {
			case 'series':
				selectedSeries.update((series) => series.filter((seriesId) => seriesId !== id));
				break;
			case 'segment':
				selectedSegments.update((segments) => segments.filter((segmentId) => segmentId !== id));
				break;
			case 'code':
				selectedCodes.update((codes) => codes.filter((codeId) => codeId !== id));
				break;
			case 'type':
				// Handle 'type' case if needed, or just break if no action is required
				break;
		}
		resetSearch();
	}

	function clearAllFilters(): void {
		selectedSeries.set([]);
		selectedSegments.set([]);
		selectedCodes.set([]);
		resetSearch();
	}

	async function addAnnotation(
		event: CustomEvent<{ elementId: number; codeId: number }>
	): Promise<void> {
		const { elementId, codeId } = event.detail;
		console.log(`Adding annotation: elementId=${elementId}, codeId=${codeId}`);
		try {
			const newAnnotation = await createAnnotation({
				element_id: elementId,
				code_id: codeId,
				project_id: $currentProject
			});

			if (newAnnotation) {
				console.log('New annotation created:', newAnnotation);
				elementsStore.update((elements) =>
					elements.map((element) => {
						if (element.element_id === elementId) {
							console.log(`Updating element ${elementId} with new annotation`);
							return {
								...element,
								annotations: [...element.annotations, newAnnotation]
							};
						}
						return element;
					})
				);
			} else {
				console.error('Failed to create annotation');
			}
		} catch (error) {
			console.error('Error adding annotation:', error);
		}
	}

	async function removeAnnotation(elementId: number, annotationId: number): Promise<void> {
		try {
			await deleteAnnotation(annotationId);
			elementsStore.update((elements) => {
				const elementIndex = elements.findIndex((el) => el.element_id === elementId);
				if (elementIndex !== -1) {
					const updatedElement = {
						...elements[elementIndex],
						annotations: elements[elementIndex].annotations.filter(
							(a) => a.annotation_id !== annotationId
						)
					};
					return [
						...elements.slice(0, elementIndex),
						updatedElement,
						...elements.slice(elementIndex + 1)
					];
				}
				return elements;
			});
		} catch (error) {
			console.error('Error removing annotation:', error);
		}
	}

	function openAnnotationDropdown(elementId: number): void {
		annotationDropdownOpen = { ...annotationDropdownOpen, [elementId]: true };
		console.log(`Opening annotation dropdown for element ${elementId}`);
	}

	function closeAnnotationDropdown(elementId: number): void {
		annotationDropdownOpen = { ...annotationDropdownOpen, [elementId]: false };
		console.log(`Closing annotation dropdown for element ${elementId}`);
	}

	function handleElementSelection(index: number, elementId: number, event: MouseEvent): void {
		let newSelectedElementIds: number[];

		if (event.shiftKey && rangeStartIndex !== -1) {
			const start = Math.min(rangeStartIndex, index);
			const end = Math.max(rangeStartIndex, index);

			newSelectedElementIds = [
				...new Set([
					...selectedElementIds,
					...$elementsStore.slice(start, end + 1).map((e) => e.element_id)
				])
			];
		} else {
			newSelectedElementIds = selectedElementIds.includes(elementId)
				? selectedElementIds.filter((id) => id !== elementId)
				: [...selectedElementIds, elementId];

			rangeStartIndex = newSelectedElementIds.includes(elementId) ? index : -1;
		}

		selectedElementIds = newSelectedElementIds;
	}

	function clearSelection(): void {
		selectedElementIds = [];
	}

	function openBatchAnnotationModal(): void {
		showBatchAnnotationModal = true;
	}

	function openBatchRemovalModal(): void {
		console.log('Opening batch removal modal');
		showBatchRemovalModal = true;
	}

	async function applyBatchAnnotations(event: CustomEvent<{ codeIds: number[] }>): Promise<void> {
		const { codeIds } = event.detail;
		if ($currentProject === null) {
			console.error('Current project is null in applyBatchAnnotations');
			return;
		}
		try {
			const newAnnotations = await createBatchAnnotations(selectedElementIds, codeIds, $currentProject);

			elementsStore.update((elements) =>
				elements.map((element) => {
					if (selectedElementIds.includes(element.element_id)) {
						const elementNewAnnotations = newAnnotations.filter(
							(annotation: Annotation) => annotation.element_id === element.element_id
						);
						return {
							...element,
							annotations: [...element.annotations, ...elementNewAnnotations]
						};
					}
					return element;
				})
			);

			clearSelection();
		} catch (error) {
			console.error('Error applying batch annotations:', error);
		}
	}

	async function handleBatchRemoval(event: CustomEvent<{ codeIds: number[] }>): Promise<void> {
		const { codeIds } = event.detail;
		const result = await removeBatchAnnotations(selectedElementIds, codeIds);
	
		if (result.success) {
			elementsStore.update((elements) => {
				return elements.map((element) => {
					if (selectedElementIds.includes(element.element_id)) {
						const updatedAnnotations = element.annotations.filter(
							(annotation) => !codeIds.includes(annotation.code?.code_id ?? -1)
						);
						return {
							...element,
							annotations: updatedAnnotations
						};
					}
					return element;
				});
			});

			// Clear selection and close modal
			clearSelection();
			showBatchRemovalModal = false;

			// Display a success message with the number of removed annotations
			alert(`Successfully removed ${result.removedCount} annotation${result.removedCount !== 1 ? 's' : ''}.`);
		} else {
			console.error('Error removing batch annotations:', result.message);
			// Display an error message to the user
			alert(`Failed to remove annotations: ${result.message}`);
		}
	}
</script>

<main>
	<h1>Content</h1>

	<div class="filters">
		<SearchBar
			value={$searchTerm}
			on:input={handleInput}
			placeholder="Search element texts..."
			debounceDelay={300}
			on:search={handleSearch}
		/>
		<FilterDropdown
			label="Filter by Series"
			options={seriesOptions}
			selected={$selectedSeries}
			on:change={handleSeriesChanged}
		/>
		<FilterDropdown
			label="Filter by Segment"
			options={segmentOptions}
			selected={$selectedSegments}
			on:change={handleSegmentChanged}
		/>
		<FilterDropdown
			label="Filter by Code"
			options={$codes.map((code) => ({
				id: code.code_id,
				name: code.term
			}))}
			selected={$selectedCodes}
			on:change={handleCodesChanged}
		/>
	</div>

	<SelectedFilters
		selectedSeries={$selectedSeries}
		selectedSegments={$selectedSegments}
		selectedCodes={$selectedCodes}
		{seriesOptions}
		{segmentOptions}
		onClearFilter={clearFilter}
		onClearAll={clearAllFilters}
	/>

	<table class:loading>
		<thead>
			<tr>
				<th>Select</th>
				<th>Series</th>
				<th>Segment</th>
				<th>Segment Title</th>
				<th>Element</th>
				<th>Codes</th>
			</tr>
		</thead>
		<tbody>
			{#each $elementsStore as element, index (element.element_id)}
				<tr transition:fade={{ duration: 100 }}>
					<td>
						<input
							type="checkbox"
							checked={selectedElementIds.includes(element.element_id)}
							on:click={(event) => handleElementSelection(index, element.element_id, event)}
							aria-label={`Select element ${element.element_id}`}
						/>
					</td>
					<td>{element.segment?.series?.series_title || 'N/A'}</td>
					<td>{element.segment?.segment_id || 'N/A'}</td>
					<td>{element.segment?.segment_title || 'N/A'}</td>
					<td>{element.element_text}</td>
					<td>
						{#each element.annotations as annotation}
							<span class="code-tag">
								{annotation.code?.term}
								<button
									class="remove-code"
									on:click={() => removeAnnotation(element.element_id, annotation.annotation_id)}
									>×</button
								>
							</span>
						{/each}
						<button class="add-code" on:click={() => openAnnotationDropdown(element.element_id)}
							>+</button
						>
						{#if annotationDropdownOpen[element.element_id]}
							<AnnotationDropdown
								isOpen={true}
								elementId={element.element_id}
								on:select={(event) => {
									addAnnotation(event);
									closeAnnotationDropdown(element.element_id);
								}}
								on:close={() => closeAnnotationDropdown(element.element_id)}
							/>
						{/if}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>

	{#if loading}
		<p>Loading more elements...</p>
	{/if}

	{#if !hasMore}
		<p>No more elements to load.</p>
	{/if}

	{#if selectedElementIds.length > 0}
		<div class="selection-bar" transition:slide={{ duration: 300, axis: 'y' }}>
			<span class="selection-count">
				{selectedElementIds.length} element{selectedElementIds.length !== 1 ? 's' : ''} selected
			</span>
			<button class="annotate-button" on:click={openBatchAnnotationModal}>
				Add Annotations
			</button>
			<button class="remove-annotations-button" on:click={() => (showBatchRemovalModal = true)}>
				Remove Annotations
			</button>
			<button class="clear-button" on:click={clearSelection}>Clear Selection</button>
		</div>
	{/if}

	<BatchAnnotationModal
		bind:show={showBatchAnnotationModal}
		selectedCount={selectedElementIds.length}
		{selectedElementIds}
		on:applyAnnotations={applyBatchAnnotations}
	/>

	<BatchRemovalModal
		bind:show={showBatchRemovalModal}
		selectedCount={selectedElementIds.length}
		selectedElements={$elementsStore.filter(element => selectedElementIds.includes(element.element_id))}
		on:removeAnnotations={handleBatchRemoval}
	/>
</main>

<style>
	.filters {
		display: flex;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		visibility: visible;
	}

	th,
	td {
		border: 1px solid #ddd;
		padding: 8px;
		text-align: left;
	}

	th {
		background-color: #4a90e2;
		color: white;
	}

	.code-tag {
		display: inline-flex;
		align-items: center;
		background-color: #e0e0e0;
		border-radius: 4px;
		padding: 2px 4px;
		margin-right: 4px;
		font-size: 0.8em;
	}

	.remove-code,
	.add-code {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.8em;
		padding: 0 2px;
	}

	.add-code {
		background-color: #4a90e2;
		color: white;
		border-radius: 50%;
		width: 20px;
		height: 20px;
		display: inline-flex;
		justify-content: center;
		align-items: center;
	}

	.selection-bar {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		background-color: #f0f0f0;
		padding: 1rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
		box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
	}

	.selection-count {
		font-weight: bold;
	}

	.annotate-button,
	.remove-annotations-button,
	.clear-button {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 1rem;
	}

	.annotate-button {
		background-color: #4a90e2;
		color: white;
	}

	.remove-annotations-button {
		background-color: #e74c3c;
		color: white;
	}

	.clear-button {
		background-color: transparent;
		color: #333;
	}

	.annotate-button:hover,
	.remove-annotations-button:hover,
	.clear-button:hover {
		opacity: 0.8;
	}

	.annotate-button:focus,
	.remove-annotations-button:focus,
	.clear-button:focus {
		outline: none;
		box-shadow: 0 0 0 2px #4a90e2;
	}
</style>
