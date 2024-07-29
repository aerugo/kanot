<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { slide } from "svelte/transition";
  import { addCode } from "../api";
  import { codeTypes, codes } from "../stores/codeStore";
  import { currentProject } from "../stores/projectStore";
  import type { Code } from "../types";

  interface NewCode {
    term: string;
    description: string;
    type_id: string;
    reference: string;
    coordinates: string;
  }

  interface ErrorResponse {
    message: string;
  }

  const dispatch = createEventDispatcher<{
    codeAdded: Code;
  }>();

  let newCode: NewCode = {
    term: "",
    description: "",
    type_id: "",
    reference: "",
    coordinates: "",
  };
  let isFormVisible: boolean = false;
  let statusMessage: string = "";
  let statusType: "success" | "error" | "" = "";

  function toggleForm(): void {
    isFormVisible = !isFormVisible;
    if (!isFormVisible) {
      resetForm();
    }
  }

  function resetForm(): void {
    newCode = {
      term: "",
      description: "",
      type_id: "",
      reference: "",
      coordinates: "",
    };
    statusMessage = "";
    statusType = "";
  }

  async function handleSubmit(): Promise<void> {
    try {
      const projectId = $currentProject;
      if (!projectId) {
        throw new Error("No project selected");
      }
      const codeWithProject = { ...newCode, project_id: projectId };
      const response: Code = await addCode(codeWithProject);
      if (response && response.code_id) {
        codes.add(response);
        resetForm();
        isFormVisible = false;
        statusMessage = "Code added successfully!";
        statusType = "success";
        dispatch("codeAdded", response);
      } else {
        throw new Error("Invalid response from server");
      }
    } catch (error: unknown) {
      console.error("Error adding code:", error);
      if (error instanceof Error) {
        if (typeof error === 'object' && error !== null && 'response' in error) {
          const errorObj = error as { response?: { data?: ErrorResponse } };
          statusMessage = errorObj.response?.data?.message || error.message;
        } else {
          statusMessage = error.message;
        }
      } else {
        statusMessage = "An unknown error occurred while adding the code";
      }
      statusType = "error";
    }
    setTimeout(() => {
      statusMessage = "";
      statusType = "";
    }, 5000);
  }
</script>

<div class="new-code-container">
	<button class="new-code-btn" on:click={toggleForm}>
		{isFormVisible ? 'Cancel' : 'New Code'}
	</button>
</div>

{#if isFormVisible}
	<section class="add-code" transition:slide={{ duration: 300 }}>
		<h2>Add New Code</h2>
		<form on:submit|preventDefault={handleSubmit}>
			<input bind:value={newCode.term} placeholder="Term" required />
			<input bind:value={newCode.description} placeholder="Description" />
			<select bind:value={newCode.type_id} required>
				<option value="">Select Code Type</option>
				{#each $codeTypes as codeType}
					<option value={codeType.type_id}>{codeType.type_name}</option>
				{/each}
			</select>
			<input bind:value={newCode.reference} placeholder="Read more" />
			<input bind:value={newCode.coordinates} placeholder="Coordinates" />
			<div class="form-buttons">
				<button type="submit">Add Code</button>
				<button type="button" class="cancel-btn" on:click={toggleForm}>Cancel</button>
			</div>
		</form>
	</section>
{/if}

{#if statusMessage}
	<div class="status-message {statusType}" transition:slide={{ duration: 300 }}>
		{statusMessage}
	</div>
{/if}

<style>
	.new-code-container {
		display: flex;
		justify-content: flex-end;
		margin-bottom: 1rem;
	}

	.new-code-btn {
		background-color: #2ecc71;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
		transition: background-color 0.3s ease;
		font-size: 1rem;
		font-weight: bold;
	}

	.new-code-btn:hover {
		background-color: #27ae60;
	}

	.add-code {
		background-color: #fff;
		border-radius: 8px;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
		padding: 2rem;
		margin-bottom: 2rem;
		animation: highlight 1s ease-out;
	}

	@keyframes highlight {
		0% {
			background-color: #e8f7f0;
		}
		100% {
			background-color: #fff;
		}
	}

	form {
		display: grid;
		gap: 1rem;
	}

	input,
	select {
		padding: 0.5rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
	}

	select {
		background-color: white;
		cursor: pointer;
	}

	select:focus {
		outline: none;
		border-color: #3498db;
	}

	.form-buttons {
		display: flex;
		justify-content: flex-end;
		gap: 1rem;
		margin-top: 1rem;
	}

	.cancel-btn {
		background-color: #95a5a6;
	}

	.cancel-btn:hover {
		background-color: #7f8c8d;
	}

	.status-message {
		padding: 10px;
		border-radius: 4px;
		margin-bottom: 10px;
		text-align: center;
	}

	.status-message.success {
		background-color: #d4edda;
		color: #155724;
		border: 1px solid #c3e6cb;
	}

	.status-message.error {
		background-color: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}
</style>
