import os
from typing import Dict
from src.knowledge.graph_store import GraphStore
from src.core.logger import logger

class GraphReporter:
    def __init__(self, vault_path: str = "vault"):
        self.output_dir = os.path.join(vault_path, "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_interactive_html(self, store: GraphStore, filename: str = "graph.html"):
        """D3.js를 사용한 인터랙티브 지식 그래프 HTML을 생성합니다."""
        json_data = store.to_json()
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Research Knowledge Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: 'Inter', sans-serif; margin: 0; background: #0f172a; color: #f8fafc; overflow: hidden; }}
        #controls {{ position: absolute; top: 20px; left: 20px; z-index: 10; background: rgba(30, 41, 59, 0.8); padding: 15px; border-radius: 12px; backdrop-filter: blur(8px); border: 1px solid #334155; }}
        #details {{ position: absolute; bottom: 20px; right: 20px; z-index: 10; background: rgba(30, 41, 59, 0.8); padding: 15px; border-radius: 12px; width: 300px; backdrop-filter: blur(8px); border: 1px solid #334155; display: none; }}
        .node {{ stroke: #1e293b; stroke-width: 2px; cursor: pointer; }}
        .link {{ stroke: #64748b; stroke-opacity: 0.4; stroke-width: 1.5; }}
        .label {{ font-size: 10px; fill: #94a3b8; pointer-events: none; }}
        h3 {{ margin: 0 0 10px 0; color: #38bdf8; }}
        .tag-EXTRACTED {{ color: #4ade80; }}
        .tag-INFERRED {{ color: #fbbf24; }}
        .tag-AMBIGUOUS {{ color: #f87171; }}
    </style>
</head>
<body>
    <div id="controls">
        <h3>Research Graph Explorer</h3>
        <p style="font-size: 12px; color: #94a3b8;">Drag to move | Scroll to zoom<br>Click nodes to see details</p>
    </div>
    <div id="details">
        <h4 id="node-name"></h4>
        <p id="node-desc" style="font-size: 13px; color: #cbd5e1;"></p>
        <hr style="border: 0.5px solid #334155;">
        <div id="rel-info" style="font-size: 12px;"></div>
    </div>
    <svg id="graph-svg"></svg>

    <script>
        const data = {json_data};
        
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("#graph-svg")
            .attr("width", width)
            .attr("height", height);
            
        const g = svg.append("g");
        
        svg.call(d3.zoom().on("zoom", (event) => {{
            g.attr("transform", event.transform);
        }}));

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const colorScale = d3.scaleOrdinal(d3.schemeTableau10);

        const link = g.append("g")
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("class", "link");

        const node = g.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", 8)
            .attr("fill", d => colorScale(d.group))
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        const label = g.append("g")
            .selectAll("text")
            .data(data.nodes)
            .join("text")
            .attr("class", "label")
            .attr("dy", -12)
            .attr("text-anchor", "middle")
            .text(d => d.id);

        node.on("click", (event, d) => {{
            d3.select("#details").style("display", "block");
            d3.select("#node-name").text(d.id + " [" + d.type + "]");
            
            let descHtml = d.description || "상세 설명 없음";
            if (d.pdf_path) {{
                // vault/raw/xxx.pdf -> /static/vault/raw/xxx.pdf
                const pdfUrl = d.pdf_path.replace(/\\\\/g, '/').replace(/^vault\\//, '/static/vault/');
                descHtml += '<p style="margin-top: 10px;"><a href="' + pdfUrl + '" target="_blank" style="color: #38bdf8; text-decoration: underline; font-weight: bold;">📄 원문 PDF 보기</a></p>';
            }}
            d3.select("#node-desc").html(descHtml);
            
            // 관계 정보 필터링
            const rels = data.links.filter(l => l.source.id === d.id || l.target.id === d.id);
            let relHtml = "<strong>Connections:</strong><ul style='padding-left: 15px;'>";
            rels.forEach(r => {{
                const other = r.source.id === d.id ? r.target.id : r.source.id;
                relHtml += "<li>" + other + " <span class='tag-" + r.tag + "'>(" + r.tag + ")</span>: " + r.rationale + "</li>";
            }});
            relHtml += "</ul>";
            d3.select("#rel-info").html(relHtml);
        }});

        simulation.on("tick", () => {{
            link.attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            node.attr("cx", d => d.x)
                .attr("cy", d => d.y);
            label.attr("x", d => d.x)
                .attr("y", d => d.y);
        }});

        function dragstarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }}
        function dragged(event) {{
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }}
        function dragended(event) {{
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }}
    </script>
</body>
</html>
"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_template)
        
        logger.info("interactive_graph_generated", path=filepath)
        return filepath

    def generate_audit_report(self, store: GraphStore, filename: str = "GRAPH_REPORT.md"):
        """그래프의 구조적 특징을 분석한 감사 리포트를 생성합니다."""
        nodes = list(store.graph.nodes(data=True))
        edges = list(store.graph.edges(data=True))
        
        # Centrality 분석
        import networkx as nx
        centrality = nx.degree_centrality(store.graph)
        god_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 신뢰도 분석
        tags = [attrs.get("tag") for _, _, attrs in edges]
        tag_counts = {t: tags.count(t) for t in set(tags)}
        
        report = f"""# 📊 Knowledge Graph Audit Report

## 1. 개요 (Overview)
- **전체 엔티티 수**: {len(nodes)}개
- **전체 관계 수**: {len(edges)}개
- **주요 클러스터 수**: {len(set(nx.get_node_attributes(store.graph, 'community').values())) if nodes else 0}개

## 2. 핵심 개념 (God Nodes)
지식 그래프 내에서 가장 높은 연결성을 가진 핵심 개념들입니다:
{chr(10).join([f"- **{node}**: 연결도 {score:.2f}" for node, score in god_nodes])}

## 3. 지식 신뢰도 분석 (Reliability Statistics)
- **직접 추출 (EXTRACTED)**: {tag_counts.get('EXTRACTED', 0)}개
- **추론됨 (INFERRED)**: {tag_counts.get('INFERRED', 0)}개
- **모호함 (AMBIGUOUS)**: {tag_counts.get('AMBIGUOUS', 0)}개

> [!NOTE]
> 'AMBIGUOUS'로 표시된 관계는 추가적인 검토나 문헌 확인이 권장됩니다.

## 4. 커뮤니티 구조 (Community Clusters)
그래프 위상 기반으로 탐지된 주요 주제군입니다:
"""
        # 커뮤니티별 샘플 노드 추가
        communities = {}
        for node, attrs in nodes:
            c_id = attrs.get("community", 0)
            if c_id not in communities: communities[c_id] = []
            communities[c_id].append(node)
            
        for c_id, members in sorted(communities.items()):
            report += f"- **Cluster {c_id}**: {', '.join(members[:5])}{' ...' if len(members) > 5 else ''}\n"
            
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
            
        logger.info("audit_report_generated", path=filepath)
        return filepath
