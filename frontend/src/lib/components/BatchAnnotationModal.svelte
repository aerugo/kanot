<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import { codes } from '../stores/codeStore';
	import AnnotationDropdown from './AnnotationDropdown.svelte';

	export let selectedCount: number = 0;
	export let show: boolean = false;
	export let elementId: string = '';

	let selectedCodes: number[] = [];
	let modalElement: HTMLDialogElement;
	let isDropdownOpen: boolean = false;
	const dispatch = createEventDispatcher<{
		applyAnnotations: { codeIds: number[] };
	}>();

	onMount(() => {
		if (modalElement) {
			if (show) {
				modalElement.showModal();
			} else {
				modalElement.close();
			}
		}
	});

	$: if (modalElement) {
		if (show) {
			modalElement.showModal();
		} else {
			modalElement.close();
		}
	}

	function closeModal(): void {
		show = false;
		selectedCodes = [];
		isDropdownOpen = false;
	}

	function addCode(event: CustomEvent<{ elementId: string; codeId: number }>): void {
		const codeId = event.detail.codeId;
		if (!selectedCodes.includes(codeId)) {
			selectedCodes = [...selectedCodes, codeId];
		}
		isDropdownOpen = false;
	}

	function removeCode(codeId: number): void {
		selectedCodes = selectedCodes.filter((id) => id !== codeId);
	}

	function applyAnnotations(): void {
		dispatch('applyAnnotations', { codeIds: selectedCodes });
		closeModal();
	}

	function toggleDropdown(): void {
		isDropdownOpen = !isDropdownOpen;
	}

	function getCodeTerm(codeId: number): string {
		return $codes.find((code) => code.code_id === codeId)?.term || '';
	}
</script>

<dialog
	bind:this={modalElement}
	on:close={() => (show = false)}
	on:cancel|preventDefault={closeModal}
>
	<form method="dialog">
		<h2 id="modal-title">
			Batch Annotate {selectedCount} Element{selectedCount !== 1 ? 's' : ''}
		</h2>
		<div class="code-selection">
			<button type="button" class="add-button" on:click={toggleDropdown}>
				{isDropdownOpen ? 'Close' : 'Add Code'}
			</button>
			{#if isDropdownOpen}
				<div class="dropdown-wrapper">
					<AnnotationDropdown on:select={addCode} isOpen={true} {elementId} />
				</div>
			{/if}
			<div class="selected-codes">
				{#each selectedCodes as codeId}
					<span class="code-tag">
						{getCodeTerm(codeId)}
						<button
							type="button"
							on:click={() => removeCode(codeId)}
							aria-label={`Remove code ${getCodeTerm(codeId)}`}>×</button
						>
					</span>
				{/each}
			</div>
		</div>
		<div class="actions">
			<button type="button" on:click={closeModal}>Cancel</button>
			<button type="button" on:click={applyAnnotations} disabled={selectedCodes.length === 0}
				>Apply</button
			>
		</div>
	</form>
</dialog>

<style>
	dialog {
	  border: none;
	  border-radius: 6px;
	  padding: 2rem;
	  max-width: 500px;
	  width: 100%;
	  max-height: 80vh;
	  overflow: visible;
	}
  
	dialog::backdrop {
	  background: rgba(0, 0, 0, 0.5);
	}
  
	form {
	  display: flex;
	  flex-direction: column;
	}
  
	.code-selection {
	  margin-top: 1rem;
	}
  
	.add-button {
	  width: 100%;
	  padding: 0.5rem;
	  margin-bottom: 0.5rem;
	  background-color: #4a90e2;
	  color: white;
	  border: none;
	  border-radius: 4px;
	  cursor: pointer;
	}
  
	.dropdown-wrapper {
	  position: relative;
	  z-index: 1010; /* Ensure the dropdown is above the modal */
	}
  
	.selected-codes {
	  display: flex;
	  flex-wrap: wrap;
	  gap: 0.5rem;
	  margin-top: 1rem;
	}
  
	.code-tag {
	  background-color: #e0e0e0;
	  border-radius: 4px;
	  padding: 2px 4px;
	  font-size: 0.8em;
	  display: flex;
	  align-items: center;
	}
  
	.code-tag button {
	  background: none;
	  border: none;
	  cursor: pointer;
	  font-size: 1.2em;
	  padding: 0 2px;
	  margin-left: 4px;
	}
  
	.actions {
	  margin-top: 1rem;
	  display: flex;
	  justify-content: flex-end;
	  gap: 1rem;
	}
  
	button {
	  padding: 0.5rem 1rem;
	  border: none;
	  border-radius: 4px;
	  cursor: pointer;
	}
  
	button:disabled {
	  opacity: 0.5;
	  cursor: not-allowed;
	}
  </style>