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
                type=rel.get("type", "related_to")
            )

    def get_mermaid(self) -> str:
        """현재 그래프를 Mermaid.js 형식으로 변환합니다."""
        mermaid = "graph TD\n"
        # 노드 스타일링 (타입별 색상 등)
        for node, attrs in self.graph.nodes(data=True):
            node_type = attrs.get("type", "concept")
            if node_type == "Method":
                mermaid += f"    class {node} methodStyle\n"
        
        # 에지 추가
        for u, v, attrs in self.graph.edges(data=True):
            rel_type = attrs.get("type", "rel")
            mermaid += f"    {u} -->|{rel_type}| {v}\n"
            
        return mermaid

    def get_communities(self) -> List[List[str]]:
        """Leiden 알고리즘 대신 NetworkX의 커뮤니티 탐지(Louvain 등)를 사용합니다."""
        # 무방향 그래프로 변환하여 탐지
        try:
            import networkx.community as nx_comm
            communities = nx_comm.louvain_communities(self.graph.to_undirected())
            return [list(c) for c in communities]
        except Exception as e:
            logger.error("community_detection_failed", error=str(e))
            return []

graph_store = GraphStore()
