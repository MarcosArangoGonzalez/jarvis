(function () {
  const svg = d3.select("#vault-graph");
  const detail = document.getElementById("graph-detail");
  const count = document.getElementById("graph-count");
  const controls = document.getElementById("graph-controls");
  const colors = {
    daily: "#1d9e75",
    projects: "#378add",
    research: "#7f77dd",
    dev: "#ba7517",
    skills: "#999992",
  };

  async function loadGraph(params) {
    const response = await fetch(`/api/vault/graph?${params.toString()}`);
    return response.json();
  }

  function render(graph) {
    svg.selectAll("*").remove();
    const bounds = svg.node().getBoundingClientRect();
    const width = bounds.width || 800;
    const height = bounds.height || 520;
    count.textContent = `${graph.nodes.length} nodos`;

    const links = graph.edges.map((edge) => ({ ...edge }));
    const nodes = graph.nodes.map((node) => ({ ...node }));
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id((node) => node.id).distance(80))
      .force("charge", d3.forceManyBody().strength(-180))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius((node) => 12 + node.links_count * 2));

    const link = svg.append("g")
      .attr("stroke", "currentColor")
      .attr("stroke-opacity", 0.18)
      .selectAll("line")
      .data(links)
      .join("line");

    const node = svg.append("g")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", (item) => Math.max(5, 6 + item.links_count * 1.8))
      .attr("fill", (item) => colors[item.folder] || colors.research)
      .attr("stroke", "rgba(255,255,255,0.45)")
      .attr("stroke-width", 1)
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    node.append("title").text((item) => item.title);
    node.on("click", function (_event, item) {
      detail.innerHTML = `<strong>${escapeHtml(item.title)}</strong><br><small>${escapeHtml(item.folder)} · ${item.links_count} links</small><br><code>${escapeHtml(item.id)}</code>`;
    });

    simulation.on("tick", function () {
      link
        .attr("x1", (item) => item.source.x)
        .attr("y1", (item) => item.source.y)
        .attr("x2", (item) => item.target.x)
        .attr("y2", (item) => item.target.y);
      node
        .attr("cx", (item) => item.x)
        .attr("cy", (item) => item.y);
    });

    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  async function refresh() {
    const params = new URLSearchParams(new FormData(controls));
    const graph = await loadGraph(params);
    render(graph);
  }

  controls.addEventListener("submit", function (event) {
    event.preventDefault();
    refresh();
  });
  window.addEventListener("resize", refresh);
  refresh();
})();
