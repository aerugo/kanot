<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { codes } from '../stores/codeStore';
    import type { Code } from '../types';
    import { clickOutside } from '../utils/helpers';

    const dispatch = createEventDispatcher<{
        select: { elementId: number; codeId: number };
        close: void;
    }>();

    export let isOpen: boolean;
    export let elementId: number;

    let searchTerm: string = '';
    let selectedIndex: number = 0;

    $: filteredCodes = ($codes as Code[]).filter((code) =>
        code.term.toLowerCase().includes(searchTerm.toLowerCase())
    );

    function selectCode(code: Code): void {
        dispatch('select', { elementId, codeId: code.code_id });
        close();
    }

    function handleKeydown(event: KeyboardEvent): void {
        if (event.key === 'ArrowDown') {
            selectedIndex = (selectedIndex + 1) % filteredCodes.length;
        } else if (event.key === 'ArrowUp') {
            selectedIndex = (selectedIndex - 1 + filteredCodes.length) % filteredCodes.length;
        } else if (event.key === 'Enter') {
            if (filteredCodes[selectedIndex]) {
                selectCode(filteredCodes[selectedIndex]);
            }
        } else if (event.key === 'Escape') {
            close();
        }
    }

    function close(): void {
        dispatch('close');
    }
</script>

{#if isOpen}
    <div class="annotation-dropdown-wrapper" use:clickOutside={close}>
        <div class="annotation-dropdown">
            <input
                type="text"
                bind:value={searchTerm}
                placeholder="Search codes..."
                on:keydown={handleKeydown}
            />
            <ul>
                {#each filteredCodes as code, index}
                    <li>
                        <button
                            type="button"
                            class:selected={index === selectedIndex}
                            on:click={() => selectCode(code)}
                        >
                            {code.term}
                        </button>
                    </li>
                {/each}
            </ul>
        </div>
    </div>
{/if}

<style>
    .annotation-dropdown-wrapper {
        position: relative;
    }

    .annotation-dropdown {
        position: absolute;
        top: 100%;
        left: 0;
        background-color: white;
        border: 1px solid #ccc;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        z-index: 1010;
        max-height: 300px;
        overflow-y: auto;
        width: 250px;
    }

    input {
        width: 100%;
        border: none;
        border-bottom: 1px solid #ccc;
        padding: 8px;
    }

    input:focus {
        outline: none;
    }

    ul {
        list-style-type: none;
        padding: 0;
        margin: 0;
    }

    li {
        padding: 0;
    }

    button {
        width: 100%;
        padding: 8px;
        border: none;
        background: none;
        text-align: left;
        cursor: pointer;
    }

    button:hover,
    button.selected {
        background-color: #f0f0f0;
    }
</style>