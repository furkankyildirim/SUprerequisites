import Course from "./Course"
import type { Filters } from "./GraphData";

export default class Term {

    #term: string;
    #courses = new Set<Course>();

    #byLetters = new Map<string, Course>();
    #byShorthand = new Map<string, Course>();
    allLetters: string[] = [];

    async populate(term: string) {
        this.#term = term;

        // const changes = await this.getFromEndpoint("changes");
        const updated = await this.getFromEndpoint("updates");
        const changes = await this.getFromEndpoint("changes");
        
        console.dir(updated)
        console.dir(changes)
        for (const full_name in updated) {
            if (Object.hasOwnProperty.call(updated, full_name)) {
                const prereq = updated[full_name];
                const course = new Course(full_name, prereq);

                this.#courses.add(course);
                this.#byLetters.set(course.letters, course);
                this.#byShorthand.set(course.shorthand, course);

                if (Object.hasOwnProperty.call(changes, full_name)) {
                    course.addOldPrerequisite(changes[full_name]["old"]);
                }
            }
        }

        this.allLetters = Array.from(new Set<string>(
            Array.from(this.#courses)
                .map(course => course.letters)
                .sort()
        ))
    }

    
    get term() {
        return this.#term;
    }

    get courses() {
        return Array.from(this.#courses);
    }
        
    get ready() {
        return this.#term ? true : false;
    }

    set ready(_) {
        return;
    }
    // #endregion
    
    getAllSubPrereqs(course: Course): Set<Course> {
        if (!course.hasPrerequisites) return new Set<Course>();
        const lookingFor = course.newPrerequisites.split(/[\&\|\(\)]/)
        const r = lookingFor.map(shorthand => this.#byShorthand.get(shorthand)).filter(x => x);
        const subCourses = r.reduce((prev, cur) => new Set<Course>([...this.getAllSubPrereqs(cur), ...prev]), new Set<Course>());
        return new Set<Course>([...subCourses, ...r]);

    }
        
    getCoursesByLetters(letters:string[]) {
        if (!letters || letters.length === 0 || !this.ready) return [];
        return Array.from(this.#courses).filter(course => letters.includes(course.letters))
    }

    getCourseByLettersAndCode(focusCourse: string): Course | null {
        const r = Array.from(this.#courses).filter(course => course.is(focusCourse))
        if (r.length > 1) throw "wtf happened";
        return r.length === 0 ? null : r[0];
    }

    getCoursesByFilter(filters: Filters) {
        return Array.from(this.#courses)
            .filter(course => course.fits(filters))
    }
        
    async getFromEndpoint(endpoint: string) {
        let r = await fetch(`/${endpoint}?term=${this.term}`);
        r = await r.json();

        return r;
    }


}