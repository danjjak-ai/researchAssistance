import arxiv
from langchain_core.tools import tool
from typing import List, Dict
import httpx
import os
from src.core.logger import logger
from src.config import settings

@tool
def search_arxiv(query: str, max_results: int = 20, year_from: int = 2023) -> List[Dict]:
    """arXiv에서 최신 논문을 검색합니다. 최근 n년 이내 논문만 반환합니다."""
    logger.info("searching_arxiv", query=query, max_results=max_results)
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    results = []
    try:
        for paper in search.results():
            if paper.published.year >= year_from:
                results.append({
                    "arxiv_id": paper.entry_id.split("/")[-1],
                    "title": paper.title,
                    "abstract": paper.summary,
                    "authors": [a.name for a in paper.authors],
                    "year": paper.published.year,
                    "pdf_url": paper.pdf_url,
                    "categories": paper.categories,
                })
    except Exception as e:
        logger.error("search_arxiv_failed", error=str(e))
    return results

def download_pdf(arxiv_id: str, download_dir: str = "vault/raw") -> str:
    """arXiv ID를 기반으로 PDF를 다운로드하고 저장 경로를 반환합니다."""
    os.makedirs(download_dir, exist_ok=True)
    paper = next(arxiv.Client().results(arxiv.Search(id_list=[arxiv_id])))
    path = paper.download_pdf(dirpath=download_dir, filename=f"{arxiv_id}.pdf")
    logger.info("pdf_downloaded", arxiv_id=arxiv_id, path=path)
    return path
