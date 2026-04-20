from src.agents.state import ResearchState
from src.knowledge.entity_extractor import extract_entities_and_relations
from src.knowledge.graph_store import GraphStore
from src.core.logger import logger

from src.agents.state import ResearchState
from src.knowledge.entity_extractor import extract_entities_and_relations
from src.knowledge.graph_store import GraphStore
from src.knowledge.graph_reporter import GraphReporter
from src.core.logger import logger

def graph_builder(state: ResearchState) -> dict:
    """합성된 지식을 기반으로 최종 지식 그래프와 인터랙티브 리포트를 생성합니다."""
    logger.info("graph_builder_started")
    
    store = GraphStore()
    reporter = GraphReporter()
    
    # 합성된 노트들로부터 엔티티와 관계 추출
    all_text = ""
    for note in state.get("synthesis_notes", []):
        all_text += f"\n\n## {note['name']}\n{note['content']}"
    
    if all_text:
        # graphify 스타일의 상세 추출 수행
        extraction_data = extract_entities_and_relations(all_text)
        store.add_entities_and_relations(extraction_data)
        
        # 소스 페이퍼 연결 추가
        for note in state.get("synthesis_notes", []):
            for source in note.get("sources", []):
                store.graph.add_node(source, type="Paper")
                store.graph.add_edge(source, note["name"], type="defines", tag="EXTRACTED", confidence=1.0)

    # 리포트 생성
    html_path = reporter.generate_interactive_html(store)
    audit_path = reporter.generate_audit_report(store)
    
    # Mermaid 코드 생성 (기존 UI 호환성 유지)
    mermaid_code = store.get_mermaid()
    
    logger.info("graph_builder_completed", html=html_path, audit=audit_path)
    
    return {
        "mermaid_code": mermaid_code,
        "graph_report_path": html_path,
        "audit_report_path": audit_path,
        "status": "completed"
    }
