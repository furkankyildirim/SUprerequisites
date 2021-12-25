<script lang="ts">
    import { toggle_class } from "svelte/internal";
    import type Course from "./classes/Course";
    import Term from "./classes/Term";
    import CourseCard from "./components/CourseCard.svelte" ;
    import Header from "./components/Header.svelte"

    let t = new Term();
    let labels: string[];
    let displayCourses: Course[];
    let selectedCourseLetters = [];
    let focusedCourse: Course;
    

    async function termSelectCallback(term) {
        // reset previous filters
        selectedCourseLetters = [];
        displayCourses = undefined;
        focusedCourse = undefined;
        
        // reset the term
        t = new Term();
        // get the term details
        await t.populate(term);
        
        // load filters 
        labels = t.allLetters
    }


    async function chooseFocusCourseCallback({detail: {course: toFocusCourse}} : CustomEvent) {
        console.log("focusing on " + toFocusCourse);
        const toFocusCourseObj = t.getCourseByLettersAndCode(toFocusCourse);
        if (!toFocusCourseObj) { 
            alert(toFocusCourse + " does not exist in this catalog!")
        } else {
            focusedCourse = toFocusCourseObj;
            displayCourses = Array.from(t.getAllSubPrereqs(focusedCourse));

        }
        
    }




</script>

<main>
    <Header callback={termSelectCallback}/>


<div class="page">
        <div id="view">
            {#if focusedCourse}
            <div class="focus-area">
                <CourseCard course={focusedCourse} on:focusCourse={chooseFocusCourseCallback}/>
            </div>
            {/if}
            {#if displayCourses}
                {#each displayCourses as course}
                    <CourseCard {course} on:focusCourse={chooseFocusCourseCallback}/>
                {/each}
            {/if}
        </div>
        <div id="filters">
            <h1>Filters</h1>
    
            {#if labels}
            <div class="input-group-text">
                <select class="form-select" multiple bind:value={selectedCourseLetters} on:change={() => displayCourses = t.getCoursesByLetters(selectedCourseLetters)}>
                    {#each labels as label}
                        <option value={label}>{label}</option>
                    {/each}
                </select>
            </div>
            {/if}
            {#if !labels}
            <p>Please choose a term from the top right!</p>
            {/if}
        </div>
</div>
    
</main>

<style>
main {
    background-color: rgba(255,255,255,.15);
	width: 100%;
	height: 100%;
}

.page {
    margin-top: 1rem;
    display: grid;
    grid-gap: 10px;
    grid-template-rows: auto;
    grid-template-columns: 8fr 3fr;
}

#view {

    padding: 1rem;
    box-sizing: border-box;
    display: grid;
    grid-auto-rows: auto;
    grid-template-columns: repeat( auto-fit, minmax(250px, 1fr) );
    grid-gap: 10px;
}

.focus-area {
    grid-column: 1 / -1;
    margin-bottom: 1rem;
}

#filters > * {
    text-align: center;
}
</style>