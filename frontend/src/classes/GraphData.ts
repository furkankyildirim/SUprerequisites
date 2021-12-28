export interface Node {
  id: string;
  isCourse: boolean;
  type?: "&" | "|";
  ghost?: boolean
}

export interface Edge {
  source: any;
  target: any;
}

export interface GraphThingsReturnType {
  nodes: Node[];
  edges: Edge[];
};

export interface Filters {
  letters: string[];
  codes: { start?: number; end?: number };
  exacts?: string[];
}

export function mergeGraphData(s: GraphThingsReturnType, t: GraphThingsReturnType) {
  t.edges = t.edges.concat(s.edges);
  t.nodes = t.nodes.concat(s.nodes);
  console.dir(t);
  return t;
}