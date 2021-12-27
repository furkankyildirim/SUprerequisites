import type { Node, Edge, Filters } from "./GraphData";

export default class Course {
  #letters: string;
  #code: string;
  #name: string;
  #newPreq: string;
  #oldPreq?: string;

  constructor(name: string, newPreq: string) {
    this.#name = name.split(" - ")[1];

    const lhs = name.split(" - ")[0].split(" ");
    this.#letters = lhs[0];
    this.#code = lhs[1];

    this.#oldPreq = newPreq;
    this.#newPreq = newPreq;
  }

  // gives us the required edges as well as the sub nodes
  get graphThings(): { nodes: Node[]; edges: Edge[] } {
    const r = {nodes: [], edges: []};

    return r;
  }

  addOldPrerequisite(oldPreq) {
    this.#oldPreq = oldPreq;
  }

  lettersAre(letters: string): boolean {
    return letters === this.#letters;
  }

  is(courseShorthand: string): boolean {
    return courseShorthand == this.shorthand;
  }

  fits(filters: Filters): boolean {
    const n = this.codeAsNumber;
    return (
      new Set(filters.exacts).has(this.shorthand) 
      || (
        new Set(filters.letters).has(this.letters)
        && (
          (!filters.codes.start || filters.codes.start <= n)
          && (!filters.codes.end || filters.codes.end >= n)
        )
      )
    )
  }

  get shorthand() {
    return this.#letters + this.#code;
  }
  get fullName() {
    return `${this.#letters} ${this.#code} - ${this.#name}`;
  }

  get letters() {
    return this.#letters;
  }

  get code() {
    return this.#code;
  }
  get codeAsNumber():number {
    return parseInt(/\d+/.exec(this.#code)[0]);
  }

  get name() {
    return this.#name;
  }

  get hasPrerequisites() {
    return this.#newPreq ? true : false;
  }

  get oldPrerequisites() {
    return this.#oldPreq;
  }

  get changed() {
    return this.#oldPreq ? true : false;
  }

  get newPrerequisites() {
    return this.#newPreq;
  }
}
