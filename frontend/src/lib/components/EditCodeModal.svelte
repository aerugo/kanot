<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import { updateCode } from "../api.ts";
  import { codeTypes } from "../stores/codeStore.ts";

  interface Code {
    code_id: number;
    term: string;
    description: string;
    type_id: number;
    reference?: string;
    coordinates?: string;
  }

  const dispatch = createEventDispatcher<{
    codeUpdated: Code;
    close: void;
  }>();

  export let code: Code | null = null;

  let editingCode: Code | null = null;
  let modalEl: HTMLDivElement;
  let firstFocusableEl: HTMLElement;
  let lastFocusableEl: HTMLElement;

  onMount(() => {
    if (code) {
      editingCode = { ...code };
    }
  });

  $: if (code && !editingCode) {
    editingCode = { ...code };
  }

  onMount(() => {
    if (modalEl) {
      const focusableElements = modalEl.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      firstFocusableEl = focusableElements[0];
      lastFocusableEl = focusableElements[focusableElements.length - 1];
      firstFocusableEl.focus();
    }
  });

  async function saveEdit() {
    if (editingCode) {
      try {
        await updateCode(editingCode.code_id, editingCode);
        dispatch("codeUpdated", editingCode);
        closeModal();
      } catch (error) {
        console.error("Error updating code:", error);
        // You might want to show an error message to the user here
      }
    }
  }

  function closeModal() {
    dispatch("close");
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Escape") {
      closeModal();
    } else if (event.key === "Tab") {
      // Trap focus
      if (event.shiftKey && document.activeElement === firstFocusableEl) {
        lastFocusableEl.focus();
        event.preventDefault();
      } else if (
        !event.shiftKey &&
        document.activeElement === lastFocusableEl
      ) {
        firstFocusableEl.focus();
        event.preventDefault();
      }
    }
  }

  function handleOverlayClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      closeModal();
    }
  }
</script>

{#if code && editingCode}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div
    class="modal-overlay"
    on:click={handleOverlayClick}
    on:keydown={handleKeydown}
    role="presentation"
  >
    <div
      class="modal"
      bind:this={modalEl}
      role="dialog"
      aria-labelledby="modal-title"
    >
      <h2 id="modal-title">Edit Code</h2>
      <form on:submit|preventDefault={saveEdit}>
        <label>
          Term:
          <input bind:value={editingCode.term} required />
        </label>
        <label>
          Description:
          <input bind:value={editingCode.description} />
        </label>
        <label>
          Code Type:
          <select bind:value={editingCode.type_id} required>
            <option value="">Select Code Type</option>
            {#each $codeTypes as codeType}
              <option value={codeType.type_id}>{codeType.type_name}</option>
            {/each}
          </select>
        </label>
        <label>
          Reference:
          <input bind:value={editingCode.reference} />
        </label>
        <label>
          Coordinates:
          <input bind:value={editingCode.coordinates} />
        </label>
        <div class="button-group">
          <button type="submit">Save</button>
          <button type="button" on:click={closeModal}>Cancel</button>
        </div>
      </form>
    </div>
  </div>
{/if}


<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .modal {
    background-color: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    max-width: 500px;
    width: 100%;
  }

  form {
    display: grid;
    gap: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
  }

  input,
  select {
    width: 100%;
    padding: 0.5rem;
    margin-top: 0.25rem;
  }

  select {
    background-color: white;
    cursor: pointer;
  }

  .button-group {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
  }

  button {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  button[type="submit"] {
    background-color: #3498db;
    color: white;
  }

  button[type="button"] {
    background-color: #95a5a6;
    color: white;
  }
</style>
