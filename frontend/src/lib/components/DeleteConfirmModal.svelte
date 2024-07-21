<script lang="ts">
    import { createEventDispatcher } from 'svelte';

    export let code: { code_id: number; term: string };

    const dispatch = createEventDispatcher();

    function confirmDelete() {
        dispatch('confirm', code.code_id);
    }

    function cancelDelete() {
        dispatch('cancel');
    }
</script>

<div class="modal-backdrop">
    <div class="modal">
        <h2>Confirm Deletion</h2>
        <p>Are you sure you want to delete the code "{code.term}"?</p>
        <p class="warning">This action cannot be undone.</p>
        <div class="button-group">
            <button class="btn btn-secondary" on:click={cancelDelete}>Cancel</button>
            <button class="btn btn-danger" on:click={confirmDelete}>Delete</button>
        </div>
    </div>
</div>

<style>
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .modal {
        background-color: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        max-width: 400px;
        width: 100%;
    }

    h2 {
        margin-top: 0;
        color: #2c3e50;
    }

    p {
        margin-bottom: 1rem;
    }

    .warning {
        color: #e74c3c;
        font-weight: bold;
    }

    .button-group {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
    }

    .btn {
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }

    .btn-secondary {
        background-color: #95a5a6;
        color: white;
    }

    .btn-secondary:hover {
        background-color: #7f8c8d;
    }

    .btn-danger {
        background-color: #e74c3c;
        color: white;
    }

    .btn-danger:hover {
        background-color: #c0392b;
    }
</style>
