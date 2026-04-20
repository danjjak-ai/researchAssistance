from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import settings
from src.agents.state import ResearchState
from src.core.logger import logger
import json
import time

def get_llm(model_name: str = None, max_retries: int = 2):
    """LLM 인스턴스를 생성합니다. 쿼터 초과 시 대체 모델로 폴백합니다."""
    return ChatGoogleGenerativeAI(
        model=model_name or settings.GEMINI_MODEL_PRIMARY,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
        max_retries=max_retries,
    )

def invoke_with_fallback(prompt: str, max_retries: int = 2):
    """Primary 모델 실패 시 Fast 모델로 폴백하고, 쿼터 초과 시 재시도합니다."""
    models_to_try = [settings.GEMINI_MODEL_PRIMARY]
    if settings.GEMINI_MODEL_FAST != settings.GEMINI_MODEL_PRIMARY:
        models_to_try.append(settings.GEMINI_MODEL_FAST)
    
    last_error = None
    for model_name in models_to_try:
        for attempt in range(max_retries + 1):
            try:
                llm = get_llm(model_name=model_name, max_retries=0)
                response = llm.invoke(prompt)
                return response
            except Exception as e:
                last_error = e
                error_str = str(e)
                
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait_time = min(2 ** attempt * 5, 60)  # 5s, 10s, 20s... max 60s
                    logger.warning("quota_exceeded_retrying", 
                                   model=model_name, attempt=attempt+1, wait=wait_time)
                    if attempt < max_retries:
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("quota_exhausted", model=model_name)
                        break  # 다음 모델로 시도
                elif "404" in error_str or "NOT_FOUND" in error_str:
                    logger.error("model_not_found", model=model_name)
                    break  # 다음 모델로 시도
                else:
                    raise  # 예상치 못한 에러는 바로 전파
    
    # 모든 모델 실패
    raise QuotaExhaustedError(
        f"모든 모델의 API 쿼터가 소진되었습니다. "
        f"Google AI Studio(https://aistudio.google.com/apikey)에서 API 키를 확인하세요. "
        f"마지막 에러: {last_error}"
    )


class QuotaExhaustedError(Exception):
    """API 쿼터 소진 시 발생하는 커스텀 에러"""
    pass


def outline_agent(state: ResearchState) -> dict:
    """사용자 입력으로부터 연구 질문과 지식 스켈레톤을 생성합니다."""
    logger.info("outline_agent_started", query=state["user_query"])
    
    prompt = f"""
    당신은 전문 연구 보조 AI입니다. 사용자의 질문을 분석하여 깊이 있는 연구를 위한 질문들로 분해하세요.
    
    사용자 질문: {state['user_query']}
    
    다음 JSON 형식으로 응답하세요:
    {{
        "research_questions": ["질문1", "질문2", ...],
        "knowledge_graph_skeleton": {{
            "nodes": [{{ "id": "ConceptA", "type": "concept" }}, ...],
            "edges": [{{ "source": "ConceptA", "target": "ConceptB", "type": "rel" }}, ...]]
        }}
    }}
    질문은 MECE(상호 배제적이고 전체 포괄적) 원칙을 따르며, 연구의 핵심을 찌르는 3~7개를 생성하세요.
    """
    
    response = invoke_with_fallback(prompt)
    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        data = json.loads(content)
        return {
            "research_questions": data.get("research_questions", []),
            "knowledge_graph": data.get("knowledge_graph_skeleton", {"nodes": [], "edges": []}),
            "status": "searching"
        }
    except json.JSONDecodeError as e:
        logger.error("outline_parsing_failed", error=str(e))
        return {
            "research_questions": [state["user_query"]],
            "status": "searching"
        }
