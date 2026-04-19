from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import settings
from src.agents.state import ResearchState
from src.core.logger import logger
import json

def get_llm(model_name: str = None):
    return ChatGoogleGenerativeAI(
        model=model_name or settings.GEMINI_MODEL_PRIMARY,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
    )

def outline_agent(state: ResearchState) -> dict:
    """사용자 입력으로부터 연구 질문과 지식 스켈레톤을 생성합니다."""
    logger.info("outline_agent_started", query=state["user_query"])
    llm = get_llm()
    
    prompt = f"""
    당신은 전문 연구 보조 AI입니다. 사용자의 질문을 분석하여 깊이 있는 연구를 위한 질문들로 분해하세요.
    
    사용자 질문: {state['user_query']}
    
    다음 JSON 형식으로 응답하세요:
    {{
        "research_questions": ["질문1", "질문2", ...],
        "knowledge_graph_skeleton": {{
            "nodes": [{{ "id": "ConceptA", "type": "concept" }}, ...],
            "edges": [{{ "source": "ConceptA", "target": "ConceptB", "type": "rel" }}, ...]
        }}
    }}
    질문은 MECE(상호 배제적이고 전체 포괄적) 원칙을 따르며, 연구의 핵심을 찌르는 3~7개를 생성하세요.
    """
    
    response = llm.invoke(prompt)
    try:
        data = json.loads(response.content)
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
