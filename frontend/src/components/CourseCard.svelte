<script lang="ts">
  import type Course from "../classes/Course";
  import CoursePreqs from "./CoursePreqs.svelte";
  import { createEventDispatcher } from 'svelte';

  const urlParams = new URLSearchParams(window.location.search);
  const useDetails = urlParams.has('details');

  export let course: Course;
  const dispatch = createEventDispatcher();
  function courseClicked(e: Event) {
        dispatch("focusCourse", {
            course: course.shorthand
        })
    }
</script>

<div class="card course-card" on:click={courseClicked} >
  <div class="card-body">
    <h5 class="card-title"><span class="course-id">{course.letters} {course.code}</span><br/><span class="course-name">{course.name}</span></h5>
    <p class="card-text">
      {#if course.changed}
          {#if useDetails}<span>Corrected Prerequisites: <CoursePreqs preqs={course.newPrerequisites} on:focusCourse/></span>
          <br/>{/if}
          <span>{#if useDetails}Original Prerequisites: {/if}<CoursePreqs preqs={course.oldPrerequisites} on:focusCourse/></span>
      {:else if course.hasPrerequisites}
          <span>Prerequisites: <CoursePreqs preqs={course.oldPrerequisites} on:course/></span>
      {:else}
          No prerequisites
      {/if}
  </p>
  
  </div>
</div>

<style>
  .course-id {
    white-space:nowrap;
  }
</style>
