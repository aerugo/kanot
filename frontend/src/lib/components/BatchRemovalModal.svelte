<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import { filteredElements } from '../stores/elementStore';
	import type { Annotation } from '../types';

	export let show = false;
	export let selectedCount: number;
	export let selectedElementIds: number[];

	const dispatch = createEventDispatcher();

	let modalElement: HTMLDialogElement;
	let selectedCodesToRemove: number[] = [];

	$: selectedElements = $filteredElements.filter((element) =>
		selectedElementIds.includes(element.element_id)
	);

	$: uniqueCodes = Array.from(
		new Set(
			selectedElements
				.flatMap((element) =>
					element.annotations
						.map((annotation) => annotation.code)
						.filter((code): code is NonNullable<Annotation['code']> => code != null)
				)
				.map((code) => JSON.stringify(code)) // Convert each code object to a string
		)
	).map((codeString) => {
		const code = JSON.parse(codeString);
		return {
			code_id: code.code_id,
			term: code.term
		};
	});

	$: if (modalElement) {
		if (show) {
			modalElement.showModal();
		} else {
			modalElement.close();
		}
	}

	onMount(() => {
		if (show && modalElement) {
			modalElement.showModal();
		}
	});

	function closeModal() {
		show = false;
		selectedCodesToRemove = [];
	}

	function toggleCode(codeId: number) {
		selectedCodesToRemove = selectedCodesToRemove.includes(codeId)
			? selectedCodesToRemove.filter((id) => id !== codeId)
			: [...selectedCodesToRemove, codeId];
	}

	function removeAnnotations() {
		dispatch('removeAnnotations', { codeIds: selectedCodesToRemove });
		closeModal();
	}
</script>

<dialog
	bind:this={modalElement}
	on:close={() => (show = false)}
	on:cancel|preventDefault={closeModal}
>
	<h2>Remove Annotations from {selectedCount} Element{selectedCount !== 1 ? 's' : ''}</h2>
	<p>Select the codes you want to remove:</p>
	<div class="code-list">
		{#each uniqueCodes as code}
			<label>
				<input
					type="checkbox"
					checked={selectedCodesToRemove.includes(code.code_id)}
					on:change={() => toggleCode(code.code_id)}
				/>
				{code.term}
			</label>
		{/each}
	</div>
	<div class="actions">
		<button on:click={closeModal}>Cancel</button>
		<button on:click={removeAnnotations} disabled={selectedCodesToRemove.length === 0}>
			Remove
		</button>
	</div>
</dialog>

<style>
	/* Add appropriate styles */
	dialog {
		border: none;
		border-radius: 6px;
		padding: 20px;
		max-width: 500px;
	}

	dialog::backdrop {
		background: rgba(0, 0, 0, 0.3);
	}

	.code-list {
		margin: 20px 0;
	}

	.actions {
		display: flex;
		justify-content: flex-end;
		gap: 10px;
	}
</style>
