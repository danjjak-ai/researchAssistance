from src.agents.state import ResearchState
from src.knowledge.entity_extractor import extract_entities_and_relations
from src.knowledge.graph_store import GraphStore
from src.core.logger import logger

def graph_builder(state: ResearchState) -> dict:
    """합성된 지식을 기반으로 최종 지식 그래프와 Mermaid 코드를 생성합니다."""
    logger.info("graph_builder_started")
    
    store = GraphStore()
    
    # 각 위키 파일 데이터에서 엔티티/관계 재추출 및 통합
    for wiki in state.get("wiki_files", []):
        # 여기서는 state에 저장된 내용을 기반으로 하거나 위키 내용을 다시 파싱할 수 있습니다.
        # 예시를 위해 synthesis_notes를 활용합니다.
        pass

    for note in state.get("synthesis_notes", []):
        # 간단한 엔티티 추가
        store.graph.add_node(note["name"], type="Concept", description=note["content"][:50])
        # 소스 관계 추가
        for source in note.get("sources", []):
            store.graph.add_node(source, type="Paper")
            store.graph.add_edge(source, note["name"], type="defines")

    # Mermaid 코드 생성
    mermaid_code = store.get_mermaid()
    
    return {
        "mermaid_code": mermaid_code,
        "status": "reviewing"
    }
