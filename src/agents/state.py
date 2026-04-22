from typing import TypedDict, Annotated, List, Dict, Optional
from langgraph.graph.message import add_messages

class ResearchState(TypedDict):
    # ── 입력 ──
    user_query: str                          # 사용자 원본 입력
    research_questions: List[str]            # Outline Agent가 생성한 하위 질문들

    # ── 검색 ──
    candidate_papers: List[Dict]             # {arxiv_id, title, abstract, year, citation_count}
    verified_papers: List[Dict]              # Semantic Scholar로 검증 완료된 논문
    pdf_paths: List[str]                     # 다운로드된 PDF 로컬 경로

    # ── 분석 ──
    parsed_markdowns: List[Dict]             # {paper_id, markdown_text, figures: list}
    synthesis_notes: List[Dict]              # {concept, content, latex_formulas, source_refs}
    ablation_findings: List[Dict]            # {method, component, effect, magnitude}

    # ── 지식 구조 ──
    knowledge_graph: Dict                    # {nodes: [...], edges: [...]}
    wiki_files: List[Dict]                   # {filename, content, backlinks: list}
    mermaid_code: str                        # 현재 그래프의 Mermaid 표현
    graph_report_path: Optional[str]         # 인터랙티브 그래프 HTML 경로
    audit_report_path: Optional[str]         # 감사 리포트 마크다운 경로

    # ── 검증 ──
    review_issues: List[Dict]               # {file, line, issue_type, severity, suggestion}
    verification_pairs: List[Dict]          # {claim, source_text, source_page, confidence}

    # ── 메타 ──
    messages: Annotated[List, add_messages]  # 에이전트 간 대화 기록
    iteration_count: int                     # 현재 반복 횟수
    max_iterations: int                      # 최대 반복 허용 횟수
    status: str                              # "planning" | "searching" | "analyzing" | "generating" | "reviewing" | "done"
