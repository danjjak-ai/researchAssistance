from src.agents.state import ResearchState
from src.core.logger import logger
from src.core.llm import invoke_with_fallback
import json


def outline_agent(state: ResearchState) -> dict:
    """사용자 입력으로부터 연구 질문과 지식 스켈레톤을 생성합니다."""
    logger.info("outline_agent_started", query=state["user_query"])
    
    prompt = f"""
    당신은 전문 연구 보조 AI입니다. 사용자의 질문을 분석하여 깊이 있는 연구를 위한 질문들로 분해하세요.
    
    사용자 질문: {state['user_query']}
    
    다음 JSON 형식으로 응답하세요 (반드시 JSON 데이터만 응답하세요):
    {{
        "research_questions": ["English search query 1", "English search query 2", ...],
        "knowledge_graph_skeleton": {{
            "nodes": [{{ "id": "ConceptA", "type": "concept" }}, ...],
            "edges": [{{ "source": "ConceptA", "target": "ConceptB", "type": "rel" }}, ...]
        }}
    }}
    
    중요:
    1. research_questions는 ArXiv 검색에 최적화되도록 반드시 영어(English)로 생성하세요.
    2. 질문은 연구의 핵심을 찌르는 3~5개를 생성하세요.
    3. JSON 형식이 깨지지 않도록 주의하세요.
    """
    
    response = invoke_with_fallback(prompt)
    try:
        from src.core.llm import clean_json_response
        content = clean_json_response(response.content)
        data = json.loads(content)
        return {
            "research_questions": data.get("research_questions", []),
            "knowledge_graph": data.get("knowledge_graph_skeleton", {"nodes": [], "edges": []}),
            "status": "searching"
        }
    except Exception as e:
        logger.error("outline_parsing_failed", error=str(e))
        return {
            "research_questions": [state["user_query"]],
            "status": "searching"
        }
