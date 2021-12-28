<script lang="ts">
  import type { Filters } from "../classes/GraphData";
  import type Term from "../classes/Term";

  export let term: Term;
  export let filters: Filters;
  export let mode;
  export let makeGraph;

  $: filters = {letters, codes: {start: parseInt(start), end: parseInt(end)}, exacts: exacts.split(/(, *)/)}

  let letters: string[] = [];
  let exacts: string = "";
  let start: string = "";
  let end: string = "";

</script>

<div id="filters">
  <h1>Filters</h1>
  {#if !term.ready}
    <p>Please choose a term from the top right!</p>
  {:else}


  <div class="part" id="mode">
    <div class="form-check form-check-inline">
      <input type="radio" class="form-check-input" name="mode" id="cardsChoice" bind:group={mode} value="cards"/>
      <label class="form-check-label" for="cardsChoice">Cards</label>
    </div>
    <div class="form-check form-check-inline">
      <input type="radio" class="form-check-input" name="mode" id="graphChoice" bind:group={mode} value="graph"/>
      <label class="form-check-label" for="graphChoice">Graph</label>
    </div>
  </div>


  <hr>


  <div class="input-group-text part" id=letters>
      <select class="form-select" multiple bind:value={letters}>
        {#each term.allLetters as label}
          <option value={label}>{label}</option>
        {/each}
      </select>
    </div>


    <div class="input-group part">
      <input type="text" class="form-control" placeholder="start" aria-label="from" bind:value={start}>
      <span class="input-group-text">-</span>
      <input type="text" class="form-control" placeholder="end" aria-label="to"bind:value={end}>
    </div>    


    <hr>

    <div class="part">
      <label for="exacts" class="form-label">Courses to include</label>
      <input type="text" class="form-control" id="exacts" placeholder="MATH101,MATH102,..." bind:value={exacts}>
    </div>

    {#if mode === "graph"}<button on:click={makeGraph} class="btn btn-secondary">Update</button> {/if}
  {/if}
</div>

<style>
  #filters {
    display: flex;
    flex-direction: column;
    width: 100%;
  }

  #filters > * {
    text-align: center;
  }


  .part {
    width: 100%;
    margin: 10px 0;
  }
</style>
