/// <reference types="@sveltejs/kit" />

// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
    namespace App {
        // interface Error {}
        // interface Locals {}
        // interface PageData {}
        // interface PageState {}
        // interface Platform {}
    }

    // Add your custom event declarations here
    interface WindowEventMap {
        clickoutside: CustomEvent;
        // Add any other custom events here
    }
}

// Declare modules without types
declare module 'lodash-es';

export { };
