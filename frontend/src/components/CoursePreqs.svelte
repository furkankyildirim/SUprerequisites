<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let preqs: string;
    function courseClicked(e: Event) {
        dispatch("focusCourse", {
            course: (e.target as HTMLElement).textContent
        })
    }


    const SPLIT_REGEX = /([\(\)\&\|])/
    function splitPreqs(preq) {
        return preq
        .split(SPLIT_REGEX)
    }
</script>

<span>
    {#each splitPreqs(preqs) as part}
        {#if part.match(/^(\w+[0-9]+)$/)}
            <span on:click={courseClicked} class="course-link">{part}</span>
        {:else}
        {part}
        {/if}
    {/each}
</span>
