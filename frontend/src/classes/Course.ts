export default class Course {
  #letters: string;
  #code: string;
  #name: string;
  #oldPreq: string;
  #newPreq?: string;

  constructor(name: string, oldPreq: string) {
    this.#name = name.split(" - ")[1];

    const lhs = name.split(" - ")[0].split(" ");
    this.#letters = lhs[0];
    this.#code = lhs[1];

    this.#newPreq = oldPreq;
    this.#oldPreq = oldPreq;
  }

  addNewPrerequisite(newPreq) {
    this.#newPreq = this.#newPreq;
  }

  lettersAre(letters: string): boolean {
    return letters === this.#letters;
  }

  is(courseShorthand: string): boolean {
    return courseShorthand == this.shorthand;
  }

  get shorthand() {
      return (this.#letters + this.#code)
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

  get name() {
    return this.#name;
  }

  get hasPrerequisites() {
    return this.#oldPreq ? true : false;
  }

  get oldPrerequisites() {
    return this.#oldPreq;
  }

  get changed() {
    return this.#newPreq ? true : false;
  }

  get newPrerequisites() {
    return this.#newPreq;
  }
}
