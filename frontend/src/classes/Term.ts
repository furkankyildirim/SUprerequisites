import Course from "./Course"

export default class Term {

    #term: string;
    #courses = new Set<Course>();

    #byLetters = new Map<string, Course>();
    #byShorthand = new Map<string, Course>();

    async populate(term: string) {
        this.#term = term;

        const prerequisites = await this.getFromEndpoint("prerequisites");
        const changes = await this.getFromEndpoint("changes");
        const updated = await this.getFromEndpoint("updates");

        for (const full_name in prerequisites) {
            if (Object.hasOwnProperty.call(prerequisites, full_name)) {
                const prereq = prerequisites[full_name];
                const course = new Course(full_name, prereq);

                this.#courses.add(course);
                this.#byLetters.set(course.letters, course);
                this.#byShorthand.set(course.shorthand, course);
            }
        }

        console.dir(this)
    }

    // #region getters
    get allLetters(): string[] {
        return Array.from(new Set<string>(
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
        const lookingFor = course.oldPrerequisites.split(/[\&\|\(\)]/)
        const r = lookingFor.map(shorthand => this.#byShorthand.get(shorthand))
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
        
    async getFromEndpoint(endpoint: string) {
        let r = await fetch(`/${endpoint}?term=${this.term}`);
        r = await r.json();

        return r;
    }


}