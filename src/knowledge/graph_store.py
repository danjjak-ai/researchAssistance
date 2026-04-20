import networkx as nx
from typing import List, Dict
import json
from src.core.logger import logger

class GraphStore:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_entities_and_relations(self, data: Dict):
        """추출된 엔티티와 관계를 그래프에 추가합니다."""
        for ent in data.get("entities", []):
            self.graph.add_node(
                ent["id"], 
                type=ent.get("type", "concept"),
                description=ent.get("description", "")
            )
        
        for rel in data.get("relationships", []):
            self.graph.add_edge(
                rel["source"], 
                rel["target"], 
                type=rel.get("type", "related_to"),
                tag=rel.get("tag", "UNKNOWN"),
                confidence=rel.get("confidence", 0.5),
                rationale=rel.get("rationale", "")
            )

    def get_mermaid(self) -> str:
        """현재 그래프를 Mermaid.js 형식으로 변환합니다."""
        mermaid = "graph TD\n"
        # 노드 스타일링
        for node, attrs in self.graph.nodes(data=True):
            node_type = attrs.get("type", "concept")
            if node_type == "Method":
                mermaid += f"    class {node} methodStyle\n"
        
        # 에지 추가
        for u, v, attrs in self.graph.edges(data=True):
            rel_type = attrs.get("type", "rel")
            tag = attrs.get("tag", "")
            label = f"{rel_type} ({tag})" if tag else rel_type
            mermaid += f"    {u} -->|{label}| {v}\n"
            
        return mermaid

    def update_communities(self):
        """Louvain 알고리즘을 사용하여 커뮤니티(클러스터)를 탐지하고 노드 속성에 추가합니다."""
        try:
            import community as community_louvain
            # Louvain은 무방향 그래프에서 동작함
            undirected_g = self.graph.to_undirected()
            if len(undirected_g.nodes) == 0:
                return
                
            partition = community_louvain.best_partition(undirected_g)
            
            for node, community_id in partition.items():
                self.graph.nodes[node]["community"] = community_id
                
            logger.info("community_detection_completed", num_communities=len(set(partition.values())))
        except Exception as e:
            logger.error("community_detection_failed", error=str(e))

    def to_json(self) -> str:
        """D3.js 등 시각화 도구에서 사용할 수 있는 JSON 형식을 반환합니다."""
        self.update_communities()
        data = {
            "nodes": [],
            "links": []
        }
        
        for node, attrs in self.graph.nodes(data=True):
            data["nodes"].append({
                "id": node,
                "group": attrs.get("community", 0),
                "type": attrs.get("type", "Concept"),
                "description": attrs.get("description", "")
            })
            
        for u, v, attrs in self.graph.edges(data=True):
            data["links"].append({
                "source": u,
                "target": v,
                "value": attrs.get("confidence", 0.5) * 10,
                "type": attrs.get("type", "related_to"),
                "tag": attrs.get("tag", ""),
                "rationale": attrs.get("rationale", "")
            })
            
        return json.dumps(data, ensure_ascii=False, indent=2)

graph_store = GraphStore()
