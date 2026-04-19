from src.agents.state import ResearchState
from src.core.logger import logger
from pathlib import Path

def parse_agent(state: ResearchState) -> dict:
    """PDF를 Markdown으로 변환합니다 (MinerU/Marker 래퍼)."""
    logger.info("parse_agent_started", pdf_count=len(state["pdf_paths"]))
    
    parsed_markdowns = []
    for pdf_path in state["pdf_paths"]:
        paper_id = Path(pdf_path).stem
        logger.info("parsing_pdf", path=pdf_path)
        
        # 실제 환경에서는 MinerU나 Marker를 호출합니다.
        # 여기서는 파일 경로와 함께 가짜 마크다운을 반환하는 예시입니다.
        # 실제 구현 시 magic-pdf나 marker-pdf 라이브러리를 사용합니다.
        
        mock_content = f"# Paper {paper_id}\n\n이 논문은 {paper_id}에 대한 분석 내용을 담고 있습니다.\n\n## Abstract\nFound in {pdf_path}..."
        
        parsed_markdowns.append({
            "paper_id": paper_id,
            "markdown_text": mock_content,
            "figures": []
        })
        
    return {
        "parsed_markdowns": parsed_markdowns,
        "status": "analyzing"
    }
