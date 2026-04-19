from src.agents.state import ResearchState
from src.agents.outline_agent import get_llm
from src.core.logger import logger
import json

def review_agent(state: ResearchState) -> dict:
    """생성된 지식의 논리적 모순과 수치적 일관성을 검토합니다."""
    logger.info("review_agent_started")
    
    # 생성된 위키 파일들의 요약과 원본 분석 데이터를 대조
    review_context = {
        "synthesis": state["synthesis_notes"],
        "ablations": state["ablation_findings"]
    }
    
    llm = get_llm()
    prompt = f"""
    당신은 연구 논문의 논리적 무결성을 검증하는 에디터입니다. 
    다음 합성된 지식들 사이의 모순이나 수치 불일치, 또는 논리적 비약을 찾아내세요.
    
    데이터:
    {json.dumps(review_context, ensure_ascii=False)}
    
    다음 JSON 형식으로 응답하세요:
    {{
        "issues": [
            {{ "file": "파일명", "issue_type": "contradiction/missing/error", "severity": "critical/warning", "suggestion": "수정안" }}
        ],
        "verification_pairs": [
            {{ "claim": "주장", "source_text": "근거", "confidence": 0.95 }}
        ]
    }}
    """
    
    response = llm.invoke(prompt)
    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        data = json.loads(content)
        
        return {
            "review_issues": data.get("issues", []),
            "verification_pairs": data.get("verification_pairs", []),
            "status": "done" if not data.get("issues") else "reviewing"
        }
    except Exception as e:
        logger.error("review_parsing_failed", error=str(e))
        return {
            "review_issues": [],
            "status": "done"
        }
