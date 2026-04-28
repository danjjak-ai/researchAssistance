from src.agents.state import ResearchState
from src.knowledge.entity_extractor import extract_entities_and_relations
from src.knowledge.graph_store import GraphStore
from src.knowledge.graph_reporter import GraphReporter
from src.core.logger import logger
import os

def graph_builder(state: ResearchState) -> dict:
    """합성된 지식을 기반으로 최종 지식 그래프와 인터랙티브 리포트를 생성합니다."""
    logger.info("graph_builder_started")
    
    store = GraphStore()
    store.load_from_disk() # 기존 데이터 로드
    
    reporter = GraphReporter()
    
    # 합성된 노트들로부터 엔티티와 관계 추출
    all_text = ""
    for note in state.get("synthesis_notes", []):
        all_text += f"\n\n## {note['name']}\n{note['content']}"
    
    if all_text:
        # graphify 스타일의 상세 추출 수행
        extraction_data = extract_entities_and_relations(all_text)
        store.add_entities_and_relations(extraction_data)
        
        # 논문 ID와 PDF 경로 매핑 생성
        paper_to_pdf = {}
        for path in state.get("pdf_paths", []):
            filename = os.path.basename(path)
            # 파일명에서 .pdf 제거하여 ID 추출 (예: 2401.12345v1.pdf -> 2401.12345v1)
            paper_id = filename.replace(".pdf", "")
            paper_to_pdf[paper_id] = path

        # 소스 페이퍼 연결 추가
        for note in state.get("synthesis_notes", []):
            for source in note.get("sources", []):
                # LLM이 'SOURCE: ' 접두어를 붙이는 경우 처리
                paper_id = source.replace("SOURCE: ", "").strip()
                pdf_path = paper_to_pdf.get(paper_id)
                
                # 논문 노드 추가 (PDF 경로 포함)
                store.graph.add_node(paper_id, type="Paper", pdf_path=pdf_path or "")
                store.graph.add_edge(paper_id, note["name"], type="defines", tag="EXTRACTED", confidence=1.0)
        
        # 변경 사항 저장
        store.save_to_disk()

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
