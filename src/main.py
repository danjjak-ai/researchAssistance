import os
from dotenv import load_dotenv
from src.agents.graph import app
from src.core.logger import logger

load_dotenv()

def run_research(query: str):
    logger.info("run_started", query=query)
    
    initial_state = {
        "user_query": query,
        "research_questions": [],
        "candidate_papers": [],
        "verified_papers": [],
        "pdf_paths": [],
        "parsed_markdowns": [],
        "synthesis_notes": [],
        "ablation_findings": [],
        "knowledge_graph": {"nodes": [], "edges": []},
        "wiki_files": [],
        "mermaid_code": "",
        "review_issues": [],
        "verification_pairs": [],
        "messages": [],
        "iteration_count": 0,
        "max_iterations": 3,
        "status": "planning"
    }
    
    # LangGraph 실행
    config = {"configurable": {"thread_id": "research_001"}}
    try:
        for event in app.stream(initial_state, config=config):
            for node_name, state_update in event.items():
                logger.info("node_completed", node=node_name)
                # 여기서 실시간 UI 업데이트 등을 수행할 수 있습니다.
        
        logger.info("run_completed")
    except Exception as e:
        logger.error("run_failed", error=str(e))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_research(sys.argv[1])
    else:
        print("사용법: python -m src.main \"연구 주제\"")
