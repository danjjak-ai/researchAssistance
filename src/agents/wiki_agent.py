from src.agents.state import ResearchState
from src.tools.obsidian_writer import write_wiki_file
from src.core.logger import logger

def wiki_agent(state: ResearchState) -> dict:
    """합성된 지식을 Obsidian 마크다운 파일로 변환하여 저장합니다."""
    logger.info("wiki_agent_started", note_count=len(state["synthesis_notes"]))
    
    wiki_files = []
    
    # 1. 각 개념별 파일 생성
    for note in state["synthesis_notes"]:
        filename = note["name"]
        content = f"# {filename}\n\n{note['content']}\n\n"
        if note.get("latex"):
            content += f"## 관련 수식\n{note['latex']}\n\n"
        
        # 해당 개념과 관련된 어블레이션 결과 요약 추가
        relevant_ablations = [
            a for a in state["ablation_findings"] if a["method"] in filename or filename in a["method"]
        ]
        if relevant_ablations:
            content += "## Ablation Analysis\n"
            content += "| 제거 요소 | 성능 변화 | 수치 |\n| --- | --- | --- |\n"
            for a in relevant_ablations:
                content += f"| {a['component']} | {a['effect']} | {a['magnitude']} |\n"
        
        result = write_wiki_file.invoke({
            "filename": filename,
            "content": content,
            "tags": ["research", "auto-generated"],
            "sources": note.get("sources", []),
            "related": [n["name"] for n in state["synthesis_notes"] if n["name"] != filename][:3]
        })
        wiki_files.append({"filename": filename, "status": result})
        
    return {
        "wiki_files": wiki_files,
        "status": "reviewing"
    }
