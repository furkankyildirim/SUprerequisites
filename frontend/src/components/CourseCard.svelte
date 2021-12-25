<script lang="ts">
  import type Course from "../classes/Course";
  import CoursePreqs from "./CoursePreqs.svelte";

  export let course: Course;
</script>

<div class="card course-card">
  <div class="card-body">
    <h5 class="card-title"><span class="course-id">{course.letters} {course.code}</span><br/><span class="course-name">{course.name}</span></h5>
    <p class="card-text">
      {#if course.changed}
          <span>Corrected Prerequisites: <CoursePreqs preqs={course.newPrerequisites} on:focusCourse/></span>
          <br/>
          <span>Original Prerequisites: <CoursePreqs preqs={course.oldPrerequisites} on:focusCourse/></span>
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
