from src.agents.state import ResearchState
from src.agents.outline_agent import invoke_with_fallback
from src.core.logger import logger
import json

def synthesis_agent(state: ResearchState) -> dict:
    """여러 논문의 내용을 결합하여 핵심 지식과 어블레이션 결과를 추출합니다."""
    logger.info("synthesis_agent_started", doc_count=len(state["parsed_markdowns"]))
    
    # 모든 논문 텍스트 결합 (Gemini의 긴 컨텍스트 창 활용)
    combined_context = "\n\n---\n\n".join([
        f"SOURCE: {m['paper_id']}\nCONTENT: {m['markdown_text']}"
        for m in state["parsed_markdowns"]
    ])
    
    prompt = f"""
    당신은 세계적인 지식 합성 전문가입니다. 다음 논문 내용들을 분석하여 통합된 지식 노드와 어블레이션 결과를 추출하세요.
    
    분석할 텍스트:
    {combined_context}
    
    다음 JSON 형식으로 응답하세요:
    {{
        "concepts": [
            {{ "name": "개념명", "content": "상세설명", "latex": "수식", "sources": ["id1", "id2"] }}
        ],
        "ablation_findings": [
            {{ "method": "방법론", "component": "제거요소", "effect": "성능변화", "magnitude": "수치" }}
        ]
    }}
    LaTeX 수식은 반드시 $ 또는 $$로 감싸세요.
    """
    
    response = invoke_with_fallback(prompt)
    try:
        # JSON 문자열 추출 (마크다운 코드 블록 제거 등 처리 필요할 수 있음)
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
            
        data = json.loads(content)
        return {
            "synthesis_notes": data.get("concepts", []),
            "ablation_findings": data.get("ablation_findings", []),
            "status": "generating"
        }
    except Exception as e:
        logger.error("synthesis_parsing_failed", error=str(e))
        return {
            "synthesis_notes": [],
            "ablation_findings": [],
            "status": "generating"
        }
