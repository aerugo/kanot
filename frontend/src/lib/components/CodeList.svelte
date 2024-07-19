<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { deleteCode } from '../api';
	import { codes } from '../stores/codeStore';
	import type { Code } from '../types';
	import { generateGoogleMapsLink, getDomain } from '../utils/helpers';

	const dispatch = createEventDispatcher<{
		editCode: Code;
	}>();

	export let filteredCodes: Code[] = [];

	let sortColumn: 'term' | 'type' = 'term';
	let sortOrder: 'asc' | 'desc' = 'asc';

	function isSortableColumn(column: string): boolean {
		return ['term', 'type'].includes(column);
	}

	function sortCodes(column: string): void {
		if (column !== 'term' && column !== 'type') return;

		if (sortColumn === column) {
			sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
		} else {
			sortColumn = column;
			sortOrder = 'asc';
		}

		$codes = $codes.sort((a: Code, b: Code) => {
			let valueA: string, valueB: string;

			if (column === 'term') {
				valueA = a.term.toLowerCase();
				valueB = b.term.toLowerCase();
			} else {
				valueA = a.code_type?.type_name.toLowerCase() || '';
				valueB = b.code_type?.type_name.toLowerCase() || '';
			}

			if (valueA < valueB) return sortOrder === 'asc' ? -1 : 1;
			if (valueA > valueB) return sortOrder === 'asc' ? 1 : -1;
			return 0;
		});
	}

	async function confirmDelete(id: number): Promise<void> {
		if (confirm('Are you sure you want to delete this code?')) {
			try {
				await deleteCode(id);
				codes.remove(id);
			} catch (error) {
				console.error('Error deleting code:', error);
				// Optionally, show an error message to the user
			}
		}
	}

	function startEditing(code: Code): void {
		dispatch('editCode', code);
	}
</script>

<div class="table-container">
	{#if filteredCodes.length === 0}
		<p class="no-results">No results found.</p>
	{:else}
		<table>
			<thead>
				<tr>
					{#each ['term', 'description', 'type', 'read more', 'coordinates', 'actions'] as column}
						<th
							class:sortable={isSortableColumn(column)}
							class:sorted-asc={sortColumn === column && sortOrder === 'asc'}
							class:sorted-desc={sortColumn === column && sortOrder === 'desc'}
							on:click={() => isSortableColumn(column) && sortCodes(column)}
						>
							{column.charAt(0).toUpperCase() + column.slice(1)}
						</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each filteredCodes as code (code.code_id)}
					<tr>
						<td>{code.term}</td>
						<td>{code.description}</td>
						<td>{code.code_type?.type_name || 'N/A'}</td>
						<td>
							{#if code.reference}
								<a href={code.reference} target="_blank" rel="noopener noreferrer">
									{getDomain(code.reference)}
								</a>
							{/if}
						</td>
						<td>
							{#if code.coordinates}
								<a
									href={generateGoogleMapsLink(code.coordinates)}
									target="_blank"
									rel="noopener noreferrer"
								>
									map
								</a>
							{/if}
						</td>
						<td class="actions">
							<button on:click={() => startEditing(code)}>Edit</button>
							<button class="delete-btn" on:click={() => confirmDelete(code.code_id)}>Delete</button
							>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div>

<style>
	.table-container {
		overflow-x: auto;
	}

	table {
		width: 100%;
		border-collapse: separate;
		border-spacing: 0;
	}

	th,
	td {
		padding: 1rem;
		text-align: left;
		border-bottom: 1px solid #ecf0f1;
	}

	th {
		background-color: #3498db;
		color: white;
		font-weight: bold;
		cursor: default;
		user-select: none;
	}

	th.sortable {
		cursor: pointer;
		position: relative;
		padding-right: 20px;
	}

	th.sortable:hover {
		background-color: #2980b9;
	}

	th.sortable::after {
		content: '⇅';
		position: absolute;
		right: 5px;
		top: 50%;
		transform: translateY(-50%);
		opacity: 0.5;
	}

	th.sortable.sorted-asc::after {
		content: '▲';
		opacity: 1;
	}

	th.sortable.sorted-desc::after {
		content: '▼';
		opacity: 1;
	}

	tr:nth-child(even) {
		background-color: #f8f9fa;
	}

	.actions {
		display: flex;
		gap: 0.5rem;
	}

	.actions button {
		font-size: 0.8rem;
		padding: 0.3rem 0.6rem;
	}

	.delete-btn {
		background-color: #e74c3c;
	}

	.delete-btn:hover {
		background-color: #c0392b;
	}

	.no-results {
		text-align: center;
		padding: 1rem;
		color: #777;
		font-style: italic;
	}
</style>
