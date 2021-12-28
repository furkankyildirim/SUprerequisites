<script lang="ts">
  import type Course from "../classes/Course";
  import CoursePreqs from "./CoursePreqs.svelte";
  import { createEventDispatcher } from 'svelte';

  const urlParams = new URLSearchParams(window.location.search);
  export let focused = false;
  export let course: Course;
  const useDetails = urlParams.has('details') && course.oldPrerequisites;
  const dispatch = createEventDispatcher();
  function courseClicked(e: Event) {
    dispatch("focusCourse", {
        course: course.shorthand
    })
  }

  function close(e: Event) {
    dispatch("unfocusCourse");
  }
</script>

<div class="card course-card" class:focused="{focused}" on:click={courseClicked} >
  {#if focused}
  <button type="button" class="btn-close close" aria-label="Close" on:click={close}></button>
  {/if}
  <div class="card-body">
    <h5 class="card-title"><span class="course-id">{course.letters} {course.code}</span><br/><span class="course-name">{course.name}</span></h5>
    <p class="card-text">
      {#if course.changed}
          {#if useDetails}<span>Corrected Prerequisites: <CoursePreqs preqs={course.newPrerequisites} on:focusCourse/></span>
          <br/>{/if}
          <span>{#if useDetails}Original Prerequisites: {/if}<CoursePreqs preqs={course.oldPrerequisites} on:focusCourse/></span>
      {:else if course.hasPrerequisites}
          <span>Prerequisites: <CoursePreqs preqs={course.newPrerequisites} on:course/></span>
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

  .course-card {
    position: relative;
  }
  
  .focused {
    grid-column: 1 / -1;
    margin-bottom: 1rem;
  }

  .close {
    position: absolute;
    top:    15px;
    right:  15px;
  }
</style>
