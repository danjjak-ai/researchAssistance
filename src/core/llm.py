from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from src.config import settings
from src.core.logger import logger
import time

class QuotaExhaustedError(Exception):
    """API 쿼터 소진 시 발생하는 커스텀 에러"""
    pass

def get_llm(model_name: str = None, max_retries: int = 3):
    """LLM 인스턴스를 생성합니다. 설정된 LLM_PROVIDER에 따라 모델을 선택합니다."""
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "ollama":
        logger.info("creating_ollama_llm", model=model_name or settings.OLLAMA_MODEL)
        return ChatOllama(
            model=model_name or settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.2,
        )
    else:
        logger.info("creating_gemini_llm", model=model_name or settings.GEMINI_MODEL_PRIMARY)
        return ChatGoogleGenerativeAI(
            model=model_name or settings.GEMINI_MODEL_PRIMARY,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.2,
            max_retries=max_retries,
        )

def invoke_with_fallback(prompt: str, max_retries: int = 3):
    """설정된 프로바이더에 따라 모델을 호출합니다. Gemini의 경우 폴백 로직을 유지합니다."""
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "ollama":
        try:
            llm = get_llm()
            return llm.invoke(prompt)
        except Exception as e:
            logger.error("ollama_invocation_failed", error=str(e))
            raise
    
    # Gemini 폴백 로직
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
                
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "503" in error_str or "UNAVAILABLE" in error_str:
                    wait_time = min(2 ** attempt * 5, 60)
                    logger.warning("quota_or_server_error_retrying", 
                                   model=model_name, attempt=attempt+1, wait=wait_time, error=error_str)
                    if attempt < max_retries:
                        time.sleep(wait_time)
                        continue
                    else:
                        break
                elif "404" in error_str or "NOT_FOUND" in error_str:
                    break
                else:
                    raise
    
    raise QuotaExhaustedError(
        f"모든 Gemini 모델의 API 쿼터가 소진되었습니다. 로컬 Ollama 사용을 고려해보세요. "
        f"마지막 에러: {last_error}"
    )
