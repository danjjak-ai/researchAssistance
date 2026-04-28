import networkx as nx
from typing import List, Dict
import json
from src.core.logger import logger

class GraphStore:
    def __init__(self, persistence_path: str = "vault/output/graph_data.json"):
        self.graph = nx.DiGraph()
        self.persistence_path = persistence_path

    def save_to_disk(self):
        """그래프 데이터를 디스크에 저장합니다."""
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        data = {
            "nodes": [(n, d) for n, d in self.graph.nodes(data=True)],
            "edges": [(u, v, d) for u, v, d in self.graph.edges(data=True)]
        }
        with open(self.persistence_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("graph_store_saved", path=self.persistence_path)

    def load_from_disk(self):
        """디스크에서 그래프 데이터를 로드합니다."""
        if not os.path.exists(self.persistence_path):
            logger.info("graph_store_not_found", path=self.persistence_path)
            return False
        
        try:
            with open(self.persistence_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.graph.clear()
            for n, d in data.get("nodes", []):
                self.graph.add_node(n, **d)
            for u, v, d in data.get("edges", []):
                self.graph.add_edge(u, v, **d)
            
            logger.info("graph_store_loaded", path=self.persistence_path)
            return True
        except Exception as e:
            logger.error("graph_store_load_failed", error=str(e))
            return False

    def add_entities_and_relations(self, data: Dict):
        """추출된 엔티티와 관계를 그래프에 추가합니다. 이미 존재하면 속성을 업데이트합니다."""
        for ent in data.get("entities", []):
            node_id = ent["id"]
            if node_id in self.graph:
                # 기존 속성에 새로운 설명 추가 등 병합 로직 (선택적)
                existing_desc = self.graph.nodes[node_id].get("description", "")
                new_desc = ent.get("description", "")
                if new_desc and new_desc not in existing_desc:
                    self.graph.nodes[node_id]["description"] = f"{existing_desc}\n{new_desc}".strip()
            else:
                self.graph.add_node(
                    node_id, 
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
            mermaid += f'    "{u}" -->|"{label}"| "{v}"\n'
            
        return mermaid

    def update_communities(self):
        """Louvain 알고리즘을 사용하여 커뮤니티(클러스터)를 탐지하고 노드 속성에 추가합니다."""
        try:
            import community as community_louvain
            # Louvain은 무방향 그래프에서 동작함
            undirected_g = self.graph.to_undirected()
            if len(undirected_g.nodes) < 2:
                for node in self.graph.nodes:
                    self.graph.nodes[node]["community"] = 0
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
                "description": attrs.get("description", ""),
                "pdf_path": attrs.get("pdf_path", "")
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

import os
graph_store = GraphStore()
