from langgraph.graph import StateGraph, START, END
from src.agents.state import ResearchState
from src.agents.outline_agent import outline_agent
from src.agents.search_agent import search_agent
from src.agents.parse_agent import parse_agent
from src.agents.synthesis_agent import synthesis_agent
from src.agents.wiki_agent import wiki_agent
from src.agents.review_agent import review_agent
from src.agents.graph_builder import graph_builder

def create_research_graph():
    workflow = StateGraph(ResearchState)

    # 노드 등록
    workflow.add_node("outline",     outline_agent)
    workflow.add_node("search",      search_agent)
    workflow.add_node("parse",       parse_agent)
    workflow.add_node("synthesize",  synthesis_agent)
    workflow.add_node("wiki_gen",    wiki_agent)
    workflow.add_node("graph_build", graph_builder)
    workflow.add_node("review",      review_agent)

    # 에지 연결 (직렬 흐름)
    workflow.add_edge(START,         "outline")
    workflow.add_edge("outline",     "search")
    workflow.add_edge("search",      "parse")
    workflow.add_edge("parse",       "synthesize")
    workflow.add_edge("synthesize",  "wiki_gen")
    workflow.add_edge("wiki_gen",    "graph_build")
    workflow.add_edge("graph_build", "review")

    # 조건부 분기 (루프 제어)
    def should_continue(state: ResearchState):
        critical_issues = [i for i in state.get("review_issues", []) if i.get("severity") == "critical"]
        
        # 반복 횟수 제한 체크
        if state.get("iteration_count", 0) >= state.get("max_iterations", 3):
            return END
            
        if critical_issues:
            # 문제를 해결하기 위해 재합성 단계로 돌아감
            return "synthesize"
        return END

    workflow.add_conditional_edges("review", should_continue)

    return workflow.compile()

# 메인 실행 루프를 위한 그래프 인스턴스
app = create_research_graph()
