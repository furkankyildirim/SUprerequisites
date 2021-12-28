<script lang=ts>
import type { SimulationNodeDatum } from "d3";

    import * as d3 from "d3";
    import { Filters, GraphThingsReturnType, mergeGraphData } from "../classes/GraphData";
    import type Term from "../classes/Term";

    export let term: Term;
    export let filters: Filters;

    let container: HTMLDivElement;
    let width;
    let height;

    export let nodeSize;

    export function makeGraph() {
        console.log("im drawing a graph")

        const data = getData();
    
        console.dir(data);

        const graph = ({
            nodes: data.nodes,
            links: data.edges
        });
    
        function clamp(x, lo, hi) {
            return x < lo ? lo : x > hi ? hi : x;
        }
        const svg = d3
            .create("svg")
            .attr("viewBox", [0, 0, width, height]);


        svg
            .append('defs')
            .append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '-0 -5 10 10')
            .attr('refX', nodeSize*.6)
            .attr("refY", 0)
            .attr('orient', 'auto')
            .attr('markerWidth', 13)
            .attr('markerHeight', 13)
            .attr('xoverflow', 'visible')
            .append('svg:path')
            .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
            .attr('fill', '#999')
            .style('stroke','none');

        const link = svg
            .selectAll(".link")
            .data(graph.links)
            .join("line")
            .classed("link", true)
            .attr('marker-end','url(#arrowhead)')

        const node = svg
            .selectAll(".node")
            .data(graph.nodes)
            .join("circle")
            .attr("r", nodeSize)
            
            .classed("node", true)
            .classed("connector", d => !d.isCourse)
            .classed("ghost", d => d.ghost)
            // @ts-ignore
            .classed("fixed", d => d.fx !== undefined);
        
        node.filter((d) => !d.isCourse).attr("r", Math.round(nodeSize/2));
        node.filter((d) => d.ghost).style("fill", "#822333");
        
        const label = svg.selectAll(".label")
            .data(graph.nodes)
            .enter()
            .append("text")
            .text(function (d) { return d.type || d.id; })
            .classed("label", true)

        
        container.hasChildNodes() ? container.childNodes[0].replaceWith(svg.node()) : container.appendChild(svg.node());
    
        const simulation = d3
            .forceSimulation()
            // @ts-ignore
            .nodes(graph.nodes)
            .force("charge", d3.forceManyBody())
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("link", d3.forceLink(graph.links).distance(nodeSize*3))
            .on("tick", tick);
            
        const drag = d3
            .drag()
            .on("start", dragstart)
            .on("drag", dragged);
            
        // @ts-ignore
        node.call(drag).on("click", click);
        
        function tick() {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            node
            // @ts-ignore
                .attr("cx", d => clamp(d.x, 0, width))
            // @ts-ignore
                .attr("cy", d => clamp(d.y, 0, height));

            label
        // @ts-ignore
                .attr("x", function(d){ return d.x; })
        // @ts-ignore
    			.attr("y", function (d) {return d.y + 3; });

        }
    
        function click(event, d) {
            delete d.fx;
            delete d.fy;
            d3.select(this).classed("fixed", false);
            simulation.alpha(1).restart();
        }
    
        function dragstart() {
            d3.select(this).classed("fixed", true);
        }
    
        function dragged(event, d) {
            d.fx = clamp(event.x, 0, width);
            d.fy = clamp(event.y, 0, height);
            simulation.alpha(1).restart();
        }

    }

    function getData() {
        const r: GraphThingsReturnType = term.getCoursesByFilter(filters).reduce((prev, course) => {
            return mergeGraphData(prev, course.graphThings)
        }, {nodes: [], edges: []} as GraphThingsReturnType);

        console.log("mapping from id to node");
        console.dir(r);
        r.edges = r.edges.map(edge => {return {
            source: r.nodes.filter(n => edge.source === n.id)[0] || (() => {const c = {id: edge.source, isCourse: true, ghost: true}; r.nodes.push(c); return c})(),
            target: r.nodes.filter(n => edge.target === n.id)[0] || (() => {const c = {id: edge.target, isCourse: true, ghost: true}; r.nodes.push(c); return c})()
        }})
        console.dir(r);
        return r;
    }

</script>

<div bind:this={container} bind:clientWidth={width} bind:clientHeight={height}>
    <svg></svg>
</div>
<style>
    div {
        width: 100%;
        height: 100%;
        box-sizing: border-box;
    }
</style>