<script lang="ts">
import { onMount } from "svelte";
import Refresh from 'svelte-icons/md/MdRefresh.svelte';

    export let callback;

    let selected;
    let loaded = false
    let terms = [];

    onMount(async () => {
        await refreshTerms()
    })


    async function refreshTerms() {
        const t = await fetch("terms");
        if (t.ok) {
            terms = (await t.json()).sort();
            loaded = true;
        } else {
            throw t.status
        }
    }

    function termSelected(e) {
        callback(selected)
    }
</script>

<header class="p-3 text-black">
    <div class="container">
        <div class="d-flex flex-wrap align-items-center justify-content-center justify-content-lg-start">
            <a href="https://www.sabanciuniv.edu/en">
                <img id="su-logo" class="" src="img/SU_logo.jpg" alt="The Sabancı University logo">
            </a>
            <span class="me-lg-auto h2 my-auto">Sabancı University Prerequisites</span>
            <form class="col-12 col-lg-auto mb-3 mb-lg-0 me-lg-3">
                <div class="input-group">
                    <span class="input-group-text">Select Term:</span>
                    <select bind:value={selected} on:change={termSelected} class="form-select form-control" aria-label="Term selector" id="term-selector" disabled={!loaded}>
                        {#each terms as term}
                        <option value={term}>
                            {["Fall", "Spring", "Summer"][parseInt(term.slice(term.length - 2))-1]} {term.slice(0, 4)}
                        </option>
                        {/each}
                    </select>
                    <button on:click={refreshTerms} class="btn btn-secondary refresh"><div class="icon"><Refresh/></div></button>
                </div>
            </form>
        </div>
    </div>
</header>



<style>
#su-logo {
    height: 60px;
    margin-right: 60px;
}

.icon {
    color: white;
    height: 26px;
    width: 26px
}

/* .sticky-top {
    top: 0;
    right: 0;
    left: 0;

    position: fixed;
}
 */
header {
    background-color: rgb(220, 220, 220);
    box-shadow: 0 0 20px #000000;
}
</style>