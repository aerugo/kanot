<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { slide } from "svelte/transition";
  import { addCode } from "../api";
  import { codeTypes, codes } from "../stores/codeStore";
  import { currentProject } from "../stores/projectStore";
  import type { Code } from "../types";
  import { clickOutside } from "../utils/helpers";

  interface NewCode {
    term: string;
    description: string;
    type_id: number;
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
    type_id: 0,
    reference: "",
    coordinates: "",
  };
  let isFormVisible: boolean = false;
  let statusMessage: string = "";
  let statusType: "success" | "error" | "" = "";
  let isDropdownOpen: boolean = false;

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
      type_id: 0,
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
      console.log("Submitting new code:", codeWithProject);
      const response: Code = await addCode(codeWithProject);
      console.log("Server response:", response);
      if (response && response.code_id) {
        console.log("Server response:", response);
        codes.update(currentCodes => {
          console.log("Current codes before update:", currentCodes);
          const updatedCodes = [...currentCodes, response];
          console.log("Updated codes:", updatedCodes);
          return updatedCodes;
        });
        resetForm();
        isFormVisible = false;
        statusMessage = "Code added successfully!";
        statusType = "success";
        dispatch("codeAdded", response);
        console.log("New code added:", response);
      } else {
        console.error("Invalid response from server:", response);
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
			<div class="custom-select" data-id="add-code-type" use:clickOutside={() => isDropdownOpen = false}>
				<div class="selected-option" role="button" tabindex="0" on:click={() => isDropdownOpen = !isDropdownOpen} on:keydown={(e) => e.key === 'Enter' && (isDropdownOpen = !isDropdownOpen)}>
					{$codeTypes.find(ct => ct.type_id === newCode.type_id)?.type_name || 'Select Code Type'}
				</div>
				{#if isDropdownOpen}
					<div class="options" role="listbox">
						{#each $codeTypes as codeType}
							<div 
								class="option"
								role="option"
								tabindex="0"
								aria-selected={newCode.type_id === codeType.type_id}
								on:click={() => {
									newCode.type_id = codeType.type_id;
									isDropdownOpen = false;
								}}
								on:keydown={(e) => {
									if (e.key === 'Enter') {
										newCode.type_id = codeType.type_id;
										isDropdownOpen = false;
									}
								}}
							>
								{codeType.type_name}
							</div>
						{/each}
					</div>
				{/if}
			</div>
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
	.custom-select {
		padding: 0.5rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
	}

	.custom-select {
		position: relative;
		width: 100%;
		background-color: white;
		cursor: pointer;
	}

	.selected-option {
		padding: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		cursor: pointer;
		background-color: white;
	}

	.options {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		background-color: white;
		border: 1px solid #ccc;
		border-top: none;
		border-radius: 0 0 4px 4px;
		max-height: 200px;
		overflow-y: auto;
		z-index: 1000;
	}

	.option {
		padding: 0.5rem;
		cursor: pointer;
	}

	.option:hover {
		background-color: #f0f0f0;
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
