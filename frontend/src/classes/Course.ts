import {
  Edge,
  Filters,
  GraphThingsReturnType,
  mergeGraphData,
  Node,
} from "./GraphData";

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

    this.#oldPreq = "";
    this.#newPreq = newPreq;
  }

  // gives us the required edges as well as the sub nodes
  get graphThings(): GraphThingsReturnType {
    const r: GraphThingsReturnType = {
      nodes: [{ id: this.shorthand, isCourse: true }],
      edges: [],
    };
    return this.hasPrerequisites ? mergeGraphData(r, this.graphOfPreq(this.shorthand, this.#newPreq.replace(/ /gi, ""), 1).r) : r;
  }

  graphOfPreq(
    source: string,
    prerequisite: string,
    c_i: number
  ): { c_i: number; r: GraphThingsReturnType } {
    let r: GraphThingsReturnType = {
      nodes: [],
      edges: [] as Edge[]
    };

    let inside = false;
    let substatement = "";
    let lastPreq = "";
    let connector: Node;
    for (let i = 0; i < prerequisite.length; i++) {
      const c = prerequisite[i];

      if (inside) {
        if (c == ")") {
          let sub: GraphThingsReturnType;
          ({ c_i, r: sub } = this.graphOfPreq("", substatement, c_i));
          r = mergeGraphData(r, sub);
          inside = false;
          substatement = "";
        } else {
          substatement += c;
        }
      } else if (c === "(") {
        inside = true;
      } else if (c === "|" || c === "&") {
        if (!connector) {
          connector = {
            id: `${this.shorthand}_${c}_${c_i}`,
            isCourse: false,
            type: c,
          };
          r.nodes.push(connector);
          // add line from the start to the end
          console.log("pushed one " + source + "->" + connector.id)
          r.edges.push({source: connector.id, target: source});
        }
        
        console.log("pushed one " + connector.id + "->" + lastPreq)
        r.edges.push({source: lastPreq, target: connector.id});
        lastPreq = "";
        c_i++;
      } else {
        lastPreq += c;
      }
    }

    // at the end, we will still have the last preq (maybe)
    if (lastPreq) {
      connector ? r.edges.push({source: lastPreq, target: connector.id}) : r.edges.push({source: lastPreq, target: source})
      console.log("pushed one " + source + "->" + lastPreq)
    }
    

    return { c_i, r };
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
      new Set(filters.exacts).has(this.shorthand) ||
      (new Set(filters.letters).has(this.letters) &&
        (!filters.codes.start || filters.codes.start <= n) &&
        (!filters.codes.end || filters.codes.end >= n))
    );
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
  get codeAsNumber(): number {
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
