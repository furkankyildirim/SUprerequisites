<script lang="ts">
    import Filter from './components/Filter.svelte';

    import type Course from "./classes/Course";
    import type { Filters } from "./classes/GraphData";
    import Term from "./classes/Term";
    import CourseCard from "./components/CourseCard.svelte" ;
    import Header from "./components/Header.svelte"
    import Graph from './components/Graph.svelte';
    // import * as d3 from "d3";

    let term = new Term();
    let filters: Filters = {letters: [], codes: {}, exacts: []};
    let displayMode: "graph" | "cards" = "cards";
    let focusedCourse: Course;
    let makeGraph;

    $: displayCourses = focusedCourse ? Array.from(term.getAllSubPrereqs(focusedCourse)) : term.getCoursesByFilter(filters);


    async function termSelectCallback(chosenTerm) {
        // reset previous filters
        filters = {letters: [], codes: {}, exacts: []};
        displayCourses = undefined;
        focusedCourse = undefined;
        
        // reset the term
        term = new Term();
        
        // get the term details
        console.log(chosenTerm)
        await term.populate(chosenTerm);
        term = term;
    }
    

    async function chooseFocusCourseCallback({detail: {course: toFocusCourse}} : CustomEvent) {
        console.log("focusing on " + toFocusCourse);
        filters = {letters: [], codes: {}, exacts: []};
        const toFocusCourseObj = term.getCourseByLettersAndCode(toFocusCourse);
        if (!toFocusCourseObj) { 
            alert(toFocusCourse + " does not exist in this catalog!")
        } else {
            focusedCourse = toFocusCourseObj;
        }
    }




</script>

<main>
    <Header callback={termSelectCallback}/>
    <div class="page">
            <div id="view">
                {#if displayMode==="graph" }
                    <Graph {term} {filters} bind:makeGraph nodeSize=24/>
                {:else}
                    {#if focusedCourse}
                        <CourseCard course={focusedCourse} on:focusCourse={chooseFocusCourseCallback} focused={true} on:unfocusCourse={() => {focusedCourse = undefined; displayCourses = undefined}}/>
                    {/if}
                    {#if displayCourses}
                        {#each displayCourses as course}
                            <CourseCard {course} on:focusCourse={chooseFocusCourseCallback}/>
                        {/each}
                    {/if}
                {/if}
            </div>
        <Filter {term} on:filterChange bind:mode={displayMode} bind:filters={filters} {makeGraph}/>
    </div>
</main>

<style>
main {
    background-color: rgba(255,255,255,.15);
	width: 100%;
	height: 100%;
    display:flex;
    flex-direction: column;
}

.page {
    margin: 1rem 1rem 0;
    display: grid;
    grid-gap: 10px;
    grid-template-rows: auto;
    grid-template-columns: 8fr 3fr;
    flex-grow: 1;
}

#view {
    padding: 1rem;
    box-sizing: border-box;
    display: grid;
    grid-auto-rows: auto;
    grid-template-columns: repeat( auto-fit, minmax(250px, 1fr) );
    grid-gap: 10px;
}

</style>