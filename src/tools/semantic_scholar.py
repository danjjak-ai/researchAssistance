import httpx
from langchain_core.tools import tool
from typing import List, Dict, Optional
from src.core.logger import logger
from src.config import settings

S2_BASE = "https://api.semanticscholar.org/graph/v1"

@tool
def verify_and_enrich_paper(arxiv_id: str) -> Optional[Dict]:
    """Semantic Scholar로 논문 실존 여부 검증 및 인용 데이터 보강."""
    logger.info("verifying_paper", arxiv_id=arxiv_id)
    url = f"{S2_BASE}/paper/ARXIV:{arxiv_id}"
    params = {"fields": "title,citationCount,influentialCitationCount,references,citations,tldr"}
    headers = {}
    if settings.SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = settings.SEMANTIC_SCHOLAR_API_KEY
    
    try:
        with httpx.Client() as client:
            resp = client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "paper_id": data.get("paperId"),
                    "title": data.get("title"),
                    "citation_count": data.get("citationCount", 0),
                    "influential_citations": data.get("influentialCitationCount", 0),
                    "tldr": data.get("tldr", {}).get("text", ""),
                    "reference_count": len(data.get("references", [])),
                }
    except Exception as e:
        logger.error("semantic_scholar_failed", arxiv_id=arxiv_id, error=str(e))
    return None

@tool
def get_recommendations(paper_id: str, limit: int = 5) -> List[Dict]:
    """Semantic Scholar Recommendations API로 관련 논문 추천."""
    url = f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{paper_id}"
    params = {"fields": "title,citationCount,externalIds", "limit": limit}
    try:
        with httpx.Client() as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                return resp.json().get("recommendedPapers", [])
    except Exception as e:
        logger.error("recommendations_failed", paper_id=paper_id, error=str(e))
    return []
