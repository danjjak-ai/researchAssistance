from src.agents.state import ResearchState
from src.tools.arxiv_tool import search_arxiv, download_pdf
from src.tools.semantic_scholar import verify_and_enrich_paper
from src.core.logger import logger
from src.config import settings

def search_agent(state: ResearchState) -> dict:
    """논문을 검색하고 교차 검증 및 다운로드를 수행합니다."""
    logger.info("search_agent_started", questions=state["research_questions"])
    
    all_candidate_papers = []
    # 각 질문별로 검색 수행
    for q in state["research_questions"]:
        papers = search_arxiv.invoke({"query": q, "max_results": 5})
        all_candidate_papers.extend(papers)
    
    # 중복 제거 (arxiv_id 기준)
    unique_candidates = {p["arxiv_id"]: p for p in all_candidate_papers}.values()
    
    verified_papers = []
    pdf_paths = []
    
    # 상위 N개 논문 검증 및 다운로드
    for paper in list(unique_candidates)[:settings.MAX_ITERATIONS * 3]: # 임의의 제한
        # Semantic Scholar 보강 (실패해도 진행)
        enriched = verify_and_enrich_paper.invoke({"arxiv_id": paper["arxiv_id"]})
        if enriched:
            paper.update(enriched)
        
        verified_papers.append(paper)
        
        try:
            # ArXiv에서 바로 다운로드 시도
            path = download_pdf(paper["arxiv_id"])
            if path:
                pdf_paths.append(path)
        except Exception as e:
            logger.warning("pdf_download_skip", arxiv_id=paper["arxiv_id"], error=str(e))
                
    return {
        "candidate_papers": list(unique_candidates),
        "verified_papers": verified_papers,
        "pdf_paths": pdf_paths,
        "status": "analyzing"
    }
