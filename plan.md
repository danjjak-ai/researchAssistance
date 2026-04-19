# Plan: 에이전틱 연구 보조 시스템 — 구현 마스터플랜

> **목표**: 연구자가 짧은 아이디어를 입력하면, AI 에이전트가 자율적으로 논문을 검색·분석·합성하여
> Obsidian 방식의 로컬 마크다운 위키를 구축해주는 **"Research Knowledge Compiler"** 를 만든다.

---

## 0. 아키텍처 총괄도

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Web UI (Gradio / FastAPI)                    │
│  ┌──────────┐  ┌─────────────────┐  ┌───────────────────────────┐  │
│  │ Idea     │  │ Knowledge       │  │ Agent Action Log          │  │
│  │ Thrower  │  │ Canvas          │  │ (SSE 실시간 스트리밍)       │  │
│  │ (Input)  │  │ (Mermaid.js)    │  │                           │  │
│  └──────────┘  └─────────────────┘  └───────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Verification Overlay — 근거 문구 ↔ 원본 PDF 대조 패널          │ │
│  └────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │ REST / WebSocket
┌────────────────────────────▼────────────────────────────────────────┐
│                   Orchestration Layer (LangGraph)                   │
│                                                                     │
│  ┌────────────┐     ┌────────────┐     ┌────────────┐              │
│  │ Supervisor │────▸│ SubGraph A │────▸│ SubGraph B │──── ...      │
│  │  (Router)  │◂────│ (Search)   │◂────│ (Analyze)  │              │
│  └────────────┘     └────────────┘     └────────────┘              │
│        │                                      │                     │
│        │  State: TypedDict + Checkpoint (PG)  │                     │
│        └──────────────────────────────────────┘                     │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Human-in-the-Loop Gate  (interrupt_before / interrupt())  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                      External Services & Storage                    │
│  ┌────────┐ ┌────────────┐ ┌────────┐ ┌───────────┐ ┌───────────┐ │
│  │ arXiv  │ │ Semantic   │ │ Gemini │ │ MinerU /  │ │ Obsidian  │ │
│  │  API   │ │ Scholar API│ │ 3.1 Pro│ │ Marker    │ │ Vault     │ │
│  └────────┘ └────────────┘ └────────┘ └───────────┘ └───────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. 프로젝트 디렉터리 구조

```
research-assistant/
├── pyproject.toml                 # uv 패키지 관리 (의존성 정의)
├── .env.example                   # API 키 템플릿
├── .env                           # (gitignore) 실제 API 키
├── CLAUDE.md                      # AI 에이전트 행동 규칙 정의
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 엔트리포인트
│   ├── config.py                  # pydantic-settings 기반 설정 로더
│   │
│   ├── agents/                    # LangGraph 에이전트 정의
│   │   ├── __init__.py
│   │   ├── graph.py               # 메인 StateGraph 조립
│   │   ├── state.py               # TypedDict 상태 스키마
│   │   ├── supervisor.py          # Supervisor Router 노드
│   │   ├── outline_agent.py       # Node 1: 연구 질문 설계
│   │   ├── search_agent.py        # Node 2: 논문 검색·검증
│   │   ├── parse_agent.py         # Node 3: PDF→Markdown 변환
│   │   ├── synthesis_agent.py     # Node 4: Full-text 합성
│   │   ├── wiki_agent.py          # Node 5: Obsidian 위키 생성
│   │   ├── review_agent.py        # Node 6: 자가 검증 & Linting
│   │   └── graph_builder.py       # Node 7: Knowledge Graph 구축
│   │
│   ├── tools/                     # 에이전트가 호출하는 도구 함수들
│   │   ├── __init__.py
│   │   ├── arxiv_tool.py          # arXiv API 래퍼
│   │   ├── semantic_scholar.py    # Semantic Scholar API 래퍼
│   │   ├── pdf_parser.py          # MinerU/Marker 호출 래퍼
│   │   ├── obsidian_writer.py     # Markdown + 백링크 파일 생성기
│   │   ├── mermaid_renderer.py    # Mermaid.js 코드 생성기
│   │   └── latex_formatter.py     # LaTeX 수식 정규화 유틸
│   │
│   ├── knowledge/                 # 지식 저장 및 그래프 관리
│   │   ├── __init__.py
│   │   ├── graph_store.py         # NetworkX/Neo4j 기반 지식 그래프
│   │   ├── vector_store.py        # ChromaDB/FAISS 벡터 인덱스
│   │   └── entity_extractor.py    # 엔티티·관계 추출 (GraphRAG)
│   │
│   ├── ui/                        # 프론트엔드
│   │   ├── __init__.py
│   │   ├── gradio_app.py          # Gradio Blocks UI 조립
│   │   ├── components/
│   │   │   ├── idea_thrower.py    # 입력 컴포넌트
│   │   │   ├── knowledge_canvas.py# Mermaid 시각화
│   │   │   ├── action_log.py      # 에이전트 실시간 로그
│   │   │   └── verification.py    # 근거 대조 오버레이
│   │   └── static/
│   │       ├── styles.css
│   │       └── mermaid-init.js
│   │
│   └── core/                      # 공통 유틸리티
│       ├── __init__.py
│       ├── logger.py              # 구조화 로깅 (structlog)
│       ├── exceptions.py          # 커스텀 예외 계층
│       └── prompts/               # 프롬프트 템플릿 (Jinja2)
│           ├── outline.j2
│           ├── synthesis.j2
│           ├── review.j2
│           └── wiki_format.j2
│
├── vault/                         # Obsidian 호환 출력 디렉터리
│   ├── raw/                       # 원본 PDF 및 미가공 텍스트
│   ├── wiki/                      # AI가 생성·관리하는 위키 문서
│   ├── _index.md                  # 마스터 인덱스
│   └── _graph.json                # 지식 그래프 직렬화
│
├── tests/
│   ├── test_agents/
│   ├── test_tools/
│   └── test_knowledge/
│
└── scripts/
    ├── run_dev.py                 # 개발 서버 실행
    └── seed_vault.py              # 샘플 데이터로 vault 초기화
```

---

## 2. LangGraph 파이프라인 상세 설계

### 2.1 상태 스키마 (`state.py`)

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class ResearchState(TypedDict):
    # ── 입력 ──
    user_query: str                          # 사용자 원본 입력
    research_questions: list[str]            # Outline Agent가 생성한 하위 질문들

    # ── 검색 ──
    candidate_papers: list[dict]             # {arxiv_id, title, abstract, year, citation_count}
    verified_papers: list[dict]              # Semantic Scholar로 검증 완료된 논문
    pdf_paths: list[str]                     # 다운로드된 PDF 로컬 경로

    # ── 분석 ──
    parsed_markdowns: list[dict]             # {paper_id, markdown_text, figures: list}
    synthesis_notes: list[dict]              # {concept, content, latex_formulas, source_refs}
    ablation_findings: list[dict]            # {method, component, effect, magnitude}

    # ── 지식 구조 ──
    knowledge_graph: dict                    # {nodes: [...], edges: [...]}
    wiki_files: list[dict]                   # {filename, content, backlinks: list}
    mermaid_code: str                        # 현재 그래프의 Mermaid 표현

    # ── 검증 ──
    review_issues: list[dict]               # {file, line, issue_type, severity, suggestion}
    verification_pairs: list[dict]          # {claim, source_text, source_page, confidence}

    # ── 메타 ──
    messages: Annotated[list, add_messages]  # 에이전트 간 대화 기록
    iteration_count: int                     # 현재 반복 횟수
    max_iterations: int                      # 최대 반복 허용 횟수 (기본: 3)
    status: str                              # "planning" | "searching" | "analyzing" | "generating" | "reviewing" | "done"
```

### 2.2 그래프 노드 상세

#### Node 1 — Outline Agent (`outline_agent.py`)
| 항목 | 내용 |
|------|------|
| **입력** | `user_query` |
| **출력** | `research_questions`, 초기 `knowledge_graph` 스켈레톤 |
| **LLM** | Gemini 3.1 Pro (reasoning mode) |
| **프롬프트 전략** | PaperCoder의 Planning 단계 적용 — 연구 질문을 MECE(Mutually Exclusive, Collectively Exhaustive) 원칙으로 분해 |
| **구체적 동작** | 1) 사용자 입력에서 핵심 키워드 추출 → 2) 해당 분야의 taxonomy 생성 → 3) 각 분류별 서브 질문 3~7개 생성 → 4) 예상 지식 노드의 초기 그래프 스켈레톤 출력 |

#### Node 2 — Search & Verify Agent (`search_agent.py`)
| 항목 | 내용 |
|------|------|
| **입력** | `research_questions` |
| **출력** | `verified_papers`, `pdf_paths` |
| **외부 API** | arXiv API (최신 preprint) + Semantic Scholar API (citation graph, SPECTER2 임베딩) |
| **구체적 동작** | 1) 각 질문별 arXiv 키워드 검색 (최근 3년 필터) → 2) Semantic Scholar로 교차 검증 (논문 존재 여부, 인용수, 영향력 지표) → 3) Recommendations API로 snowballing 확장 → 4) 상위 k편(기본 10) 선별 → 5) PDF 다운로드 → `vault/raw/` 저장 |
| **중복 방지** | arxiv_id 기반 해시로 이미 처리된 논문 스킵 |

#### Node 3 — Parse Agent (`parse_agent.py`)
| 항목 | 내용 |
|------|------|
| **입력** | `pdf_paths` |
| **출력** | `parsed_markdowns` |
| **도구** | MinerU (LaTeX 정밀도 우선) → Marker (fallback, 구조 보존 우선) |
| **구체적 동작** | 1) PDF → Clean Markdown 변환 (수식은 `$...$`/`$$...$$` 보존) → 2) 그림/도표 캡션 추출 및 `![figure](path)` 형태로 임베드 → 3) 헤더/푸터/페이지번호 → 4) 섹션 구조(Introduction, Method, Results, Discussion) 자동 태깅 |
| **GPU 가속** | MinerU의 수식 인식 모델은 CUDA 필요, CPU fallback은 Marker 사용 |

#### Node 4 — Synthesis Agent (`synthesis_agent.py`)
| 항목 | 내용 |
|------|------|
| **입력** | `parsed_markdowns`, `research_questions` |
| **출력** | `synthesis_notes`, `ablation_findings` |
| **LLM** | Gemini 3.1 Pro (2M 토큰 컨텍스트 활용) |
| **프롬프트 전략** | Long-Context Synthesis — 논문 전문(full-text) 여러 편을 단일 프롬프트에 주입하여 교차 분석 |
| **구체적 동작** | 1) 논문 2~5편을 하나의 프롬프트에 결합 → 2) 각 논문에서 핵심 개념(Concept), 방법론(Method), 결과(Finding) 추출 → 3) 논문 간 공통점/차이점 비교 매트릭스 생성 → 4) Ablation Study 결과에서 인과 관계 추출 → 5) LaTeX 수식은 원본 그대로 보존 |
| **출력 형식** | 구조화된 JSON → Markdown 변환 파이프라인 |

#### Node 5 — Wiki Generation Agent (`wiki_agent.py`)
| 항목 | 내용 |
|------|------|
| **입력** | `synthesis_notes`, `ablation_findings`, `knowledge_graph` |
| **출력** | `wiki_files`, 업데이트된 `knowledge_graph` |
| **출력 경로** | `vault/wiki/` |
| **구체적 동작** | 1) 각 개념 노드를 독립 마크다운 파일로 생성 (예: `Attention_Mechanism.md`) → 2) YAML Frontmatter 자동 삽입 (`tags`, `created`, `sources`, `related`) → 3) Obsidian 백링크(`[[Link]]`) 자동 연결 → 4) 마스터 인덱스(`_index.md`) 갱신 → 5) Mermaid 그래프 코드 생성 |
| **파일 포맷** | |
```markdown
---
tags: [attention, transformer, ablation]
created: 2026-04-19
sources: ["arxiv:2301.xxxxx", "arxiv:2305.xxxxx"]
related: ["[[Positional_Encoding]]", "[[Multi_Head_Attention]]"]
---
# Attention Mechanism
## 핵심 개념
...
## Ablation 분석
| 제거 요소 | 성능 변화 | 출처 |
|-----------|----------|------|
| ...       | ...      | ...  |
## 관련 수식
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
```

#### Node 6 — Review Agent (`review_agent.py`)
| 항목 | 내용 |
|------|------|
| **입력** | `wiki_files`, `parsed_markdowns` |
| **출력** | `review_issues`, `verification_pairs` |
| **LLM** | Gemini 3.1 Pro |
| **구체적 동작** | 1) **수치 일관성 검사**: 파일 A와 B에서 동일 지표의 수치가 불일치하는지 탐지 → 2) **논리 모순 검출**: 인과 관계 주장 간의 불일치 식별 → 3) **근거 검증(Grounding)**: 각 claim을 원본 PDF의 정확한 페이지·문단과 매칭 → 4) **커버리지 분석**: research_questions 중 아직 미답변 항목 식별 → 5) severity 라벨링 (critical / warning / info) |
| **Human-in-the-Loop** | critical 이슈 발견 시 `interrupt()` 호출 → UI에 검토 요청 표시 → 사용자 승인 후 재개 |

#### Node 7 — Knowledge Graph Builder (`graph_builder.py`)
| 항목 | 내용 |
|------|------|
| **입력** | `wiki_files`, `synthesis_notes` |
| **출력** | `knowledge_graph` (확장), `mermaid_code` |
| **도구** | NetworkX (로컬) 또는 Neo4j (확장 시) |
| **구체적 동작** | 1) 위키 파일에서 엔티티(개념, 방법론, 데이터셋, 저자) 추출 → 2) 관계 유형 분류 (uses, extends, contradicts, improves) → 3) GraphRAG의 Leiden 알고리즘으로 커뮤니티 탐지 → 4) 커뮤니티별 요약 생성 → 5) Mermaid.js 코드로 변환 |

### 2.3 그래프 흐름 & 루프 제어

```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(ResearchState)

# 노드 등록
workflow.add_node("outline",     outline_agent)
workflow.add_node("search",      search_agent)
workflow.add_node("parse",       parse_agent)
workflow.add_node("synthesize",  synthesis_agent)
workflow.add_node("wiki_gen",    wiki_agent)
workflow.add_node("review",      review_agent)
workflow.add_node("graph_build", graph_builder)

# 직렬 흐름
workflow.add_edge(START,         "outline")
workflow.add_edge("outline",     "search")
workflow.add_edge("search",      "parse")
workflow.add_edge("parse",       "synthesize")
workflow.add_edge("synthesize",  "wiki_gen")
workflow.add_edge("wiki_gen",    "graph_build")
workflow.add_edge("graph_build", "review")

# 조건부 루프: review 결과에 따라 분기
def should_continue(state: ResearchState) -> str:
    critical_issues = [i for i in state["review_issues"] if i["severity"] == "critical"]
    if critical_issues and state["iteration_count"] < state["max_iterations"]:
        return "synthesize"      # 재분석 루프
    elif state["review_issues"] and state["iteration_count"] < state["max_iterations"]:
        return "wiki_gen"        # 위키만 재생성
    else:
        return END               # 완료

workflow.add_conditional_edges("review", should_continue)

# 컴파일 — 체크포인터는 부모 그래프에만 할당
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(POSTGRES_URL)

app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["review"],  # review 전 항상 사용자 확인 가능
)
```

---

## 3. 기술 스택 상세

| 계층 | 기술 | 버전/사양 | 선택 근거 |
|------|------|----------|----------|
| **Orchestration** | LangGraph | ≥ 0.3.x | 순환형 그래프, 체크포인팅, 서브그래프 조합에 최적화 |
| **LLM (주)** | Gemini 3.1 Pro | 2M 토큰 컨텍스트 | 논문 전문 다중 분석에 필수적인 초장문 컨텍스트 |
| **LLM (보조)** | Gemini 3.1 Flash | — | 엔티티 추출, 분류 등 가벼운 작업에 비용 절감 |
| **PDF 파싱** | MinerU + Marker | MinerU 기본, Marker fallback | MinerU: LaTeX 정밀도 / Marker: 범용 구조 보존 |
| **벡터 DB** | ChromaDB | 로컬 모드 | Local-First 원칙 준수, 설치 간편 |
| **그래프 DB** | NetworkX (기본) → Neo4j (확장) | — | 초기 경량 → 프로덕션 시 Neo4j로 마이그레이션 |
| **시각화** | Mermaid.js | — | Obsidian 네이티브 지원, 브라우저 렌더링 |
| **Web UI** | Gradio Blocks + FastAPI | Gradio 5.x | SSE 스트리밍, 커스텀 JS 삽입 가능 |
| **상태 저장** | PostgreSQL | — | LangGraph 체크포인트 영속화 |
| **패키지 관리** | uv | — | 빠른 의존성 해결, `.venv` 표준 사용 |
| **로깅** | structlog | — | 구조화 로그로 에이전트 디버깅 용이 |
| **프롬프트** | Jinja2 템플릿 | — | 프롬프트 버전 관리 및 재사용성 |

---

## 4. UI 구현 상세 (uix.md 매핑)

### 4.1 The Idea Thrower — 입력 컴포넌트

```python
# src/ui/components/idea_thrower.py
import gradio as gr

def create_idea_thrower():
    with gr.Column(scale=1):
        gr.Markdown("## 💡 아이디어를 던져보세요")
        query_input = gr.Textbox(
            placeholder="예: Transformer의 어블레이션 연구들 정리해줘",
            lines=3,
            label="연구 주제 또는 질문",
        )
        file_input = gr.File(
            label="📎 연구 로그/PDF 드래그 앤 드롭",
            file_types=[".pdf", ".md", ".txt"],
            file_count="multiple",
        )
        submit_btn = gr.Button("🚀 분석 시작", variant="primary", size="lg")
    return query_input, file_input, submit_btn
```

### 4.2 Knowledge Canvas — Mermaid 그래프 시각화

```python
# src/ui/components/knowledge_canvas.py
import gradio as gr

def create_knowledge_canvas():
    with gr.Column(scale=2):
        gr.Markdown("## 🧠 Knowledge Canvas")
        mermaid_display = gr.HTML(
            label="지식 그래프",
            elem_id="knowledge-graph-container",
        )
        # 노드 클릭 → 해당 wiki 파일 내용 표시
        detail_panel = gr.Markdown(
            label="노드 상세",
            elem_id="node-detail-panel",
        )
    return mermaid_display, detail_panel
```

### 4.3 Agent Action Log — 실시간 스트리밍

```python
# src/ui/components/action_log.py
import gradio as gr

def create_action_log():
    with gr.Column(scale=1):
        gr.Markdown("## 🤖 Agent Activity")
        log_display = gr.Chatbot(
            label="에이전트 활동 로그",
            type="messages",
            height=500,
            avatar_images=(None, "🔬"),
        )
        status_indicator = gr.Markdown("⏳ 대기 중...")
    return log_display, status_indicator
```

### 4.4 Verification Overlay — 근거 검증 패널

```python
# src/ui/components/verification.py
import gradio as gr

def create_verification_overlay():
    with gr.Accordion("🔍 근거 검증 (Verification)", open=False):
        with gr.Row():
            claim_display = gr.Markdown(label="AI 생성 주장")
            source_display = gr.Markdown(label="원본 근거 문구")
        confidence_bar = gr.Slider(
            0, 100, label="근거 신뢰도 (%)", interactive=False
        )
        approve_btn = gr.Button("✅ 승인", variant="primary")
        reject_btn = gr.Button("❌ 수정 요청", variant="stop")
    return claim_display, source_display, confidence_bar, approve_btn, reject_btn
```

---

## 5. 핵심 도구(Tool) 구현 명세

### 5.1 arXiv 검색 도구

```python
# src/tools/arxiv_tool.py
import arxiv
from langchain_core.tools import tool

@tool
def search_arxiv(query: str, max_results: int = 20, year_from: int = 2023) -> list[dict]:
    """arXiv에서 최신 논문을 검색합니다. 최근 3년 이내 논문만 반환합니다."""
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    results = []
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
    return results
```

### 5.2 Semantic Scholar 검증 도구

```python
# src/tools/semantic_scholar.py
import httpx
from langchain_core.tools import tool

S2_BASE = "https://api.semanticscholar.org/graph/v1"

@tool
def verify_and_enrich_paper(arxiv_id: str) -> dict | None:
    """Semantic Scholar로 논문 실존 여부 검증 및 인용 데이터 보강."""
    url = f"{S2_BASE}/paper/ARXIV:{arxiv_id}"
    params = {"fields": "title,citationCount,influentialCitationCount,references,citations,tldr"}
    resp = httpx.get(url, params=params, headers={"x-api-key": S2_API_KEY})
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
    return None

@tool
def get_recommendations(paper_id: str, limit: int = 5) -> list[dict]:
    """Semantic Scholar Recommendations API로 관련 논문 추천."""
    url = f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{paper_id}"
    params = {"fields": "title,citationCount,externalIds", "limit": limit}
    resp = httpx.get(url, params=params)
    if resp.status_code == 200:
        return resp.json().get("recommendedPapers", [])
    return []
```

### 5.3 Obsidian Wiki 생성 도구

```python
# src/tools/obsidian_writer.py
from pathlib import Path
from datetime import date
from langchain_core.tools import tool

VAULT_DIR = Path("vault/wiki")

@tool
def write_wiki_file(
    filename: str,
    content: str,
    tags: list[str],
    sources: list[str],
    related: list[str],
) -> str:
    """Obsidian 호환 마크다운 파일을 vault/wiki에 생성합니다."""
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    
    frontmatter = f"""---
tags: {tags}
created: {date.today().isoformat()}
sources: {sources}
related: {[f'[[{r}]]' for r in related]}
---
"""
    filepath = VAULT_DIR / f"{filename}.md"
    filepath.write_text(frontmatter + content, encoding="utf-8")
    
    # 마스터 인덱스 갱신
    _update_index(filename, tags)
    return f"✅ {filepath} 생성 완료"

def _update_index(filename: str, tags: list[str]):
    index_path = VAULT_DIR.parent / "_index.md"
    entry = f"- [[{filename}]] — {', '.join(tags)}\n"
    with open(index_path, "a", encoding="utf-8") as f:
        f.write(entry)
```

---

## 6. 실행 단계 (Phase별 로드맵)

### Phase 1: 기반 구축 (1~2주)
| 태스크 | 구체적 작업 | 완료 기준 |
|--------|-----------|----------|
| **P1-1** 환경 설정 | `uv init`, `.venv` 생성, pyproject.toml 의존성 정의 | `uv sync` 성공 |
| **P1-2** 설정 로더 | `config.py` — API 키, vault 경로, LLM 모델명을 `.env`에서 로드 | pydantic-settings 검증 통과 |
| **P1-3** 상태 스키마 | `state.py` — TypedDict 정의, 직렬화/역직렬화 테스트 | pytest 통과 |
| **P1-4** 프롬프트 템플릿 | `prompts/` — 각 에이전트용 Jinja2 템플릿 초안 작성 | 렌더링 확인 |
| **P1-5** 로깅 기반 | `logger.py` — structlog 설정, 에이전트별 컨텍스트 바인딩 | 로그 출력 확인 |

### Phase 2: 핵심 에이전트 (2~3주)
| 태스크 | 구체적 작업 | 완료 기준 |
|--------|-----------|----------|
| **P2-1** Outline Agent | 사용자 입력 → 연구 질문 분해 구현 | 3개 이상의 의미있는 서브질문 생성 |
| **P2-2** Search Agent | arXiv + Semantic Scholar 통합 검색 | 검증된 논문 리스트 반환, 중복 제거 |
| **P2-3** Parse Agent | MinerU/Marker PDF→MD 파이프라인 | LaTeX 수식 보존률 95% 이상 |
| **P2-4** Synthesis Agent | 다중 논문 교차 분석 | 개념별 노트 + Ablation 표 생성 |
| **P2-5** Wiki Agent | Obsidian 파일 생성 + 백링크 | vault/wiki/ 에 유효한 MD 파일 생성 |

### Phase 3: 자가 검증 루프 (1~2주)
| 태스크 | 구체적 작업 | 완료 기준 |
|--------|-----------|----------|
| **P3-1** Review Agent | 수치/논리 모순 탐지 + 근거 매칭 | 의도적 오류 3건 이상 탐지 |
| **P3-2** LangGraph 루프 | 조건부 재분석 루프 구현 | critical 이슈 시 재합성 → 해결 후 완료 |
| **P3-3** Human-in-the-Loop | interrupt() 기반 사용자 개입 | UI에서 승인/거부 후 재개 동작 확인 |

### Phase 4: 지식 그래프 & 시각화 (1~2주)
| 태스크 | 구체적 작업 | 완료 기준 |
|--------|-----------|----------|
| **P4-1** Entity Extractor | GraphRAG 방식 엔티티·관계 추출 | 논문 10편에서 유의미한 그래프 생성 |
| **P4-2** Graph Builder | NetworkX 그래프 + Leiden 커뮤니티 탐지 | 커뮤니티별 요약 생성 |
| **P4-3** Mermaid 렌더러 | 그래프 → Mermaid.js 코드 변환 | Knowledge Canvas에 실시간 표시 |
| **P4-4** Verification Overlay | 근거 대조 UI 구현 | claim ↔ source 페어 표시 + 신뢰도 |

### Phase 5: UI 통합 & 폴리싱 (1~2주)
| 태스크 | 구체적 작업 | 완료 기준 |
|--------|-----------|----------|
| **P5-1** Gradio 조립 | 4개 컴포넌트 통합, SSE 스트리밍 연결 | 전체 워크플로 E2E 시연 |
| **P5-2** 에이전트 로그 스트리밍 | LangGraph callback → SSE → Action Log | 실시간 상태 업데이트 표시 |
| **P5-3** Obsidian 연동 테스트 | 생성된 vault를 Obsidian으로 열기 | 백링크/그래프뷰 정상 표시 |
| **P5-4** LaTeX 보존 검증 | MathJax/KaTeX 렌더링 테스트 | 수식 깨짐 0건 |
| **P5-5** Offline 모드 | 한 번 분석된 데이터의 로컬 캐시 조회 | 인터넷 차단 상태에서 기존 위키 조회 가능 |

---

## 7. 환경 변수 명세 (`.env.example`)

```env
# ── LLM ──
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL_PRIMARY=gemini-3.1-pro
GEMINI_MODEL_FAST=gemini-3.1-flash

# ── 외부 API ──
SEMANTIC_SCHOLAR_API_KEY=your_s2_api_key

# ── 데이터베이스 ──
POSTGRES_URL=postgresql://user:pass@localhost:5432/research_assistant
CHROMA_PERSIST_DIR=./data/chroma

# ── 경로 ──
VAULT_DIR=./vault
RAW_DIR=./vault/raw
WIKI_DIR=./vault/wiki

# ── 파싱 ──
PDF_PARSER_PRIMARY=mineru       # mineru | marker
PDF_PARSER_FALLBACK=marker
USE_GPU=true

# ── 앱 ──
APP_HOST=0.0.0.0
APP_PORT=7860
MAX_ITERATIONS=3
LOG_LEVEL=INFO
```

---

## 8. 의존성 목록 (`pyproject.toml` 핵심)

```toml
[project]
name = "research-assistant"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # Orchestration
    "langgraph>=0.3.0",
    "langchain-google-genai>=2.0.0",
    "langchain-core>=0.3.0",

    # External APIs
    "arxiv>=2.1.0",
    "httpx>=0.27.0",

    # PDF Parsing
    "magic-pdf[full]>=0.9.0",       # MinerU
    "marker-pdf>=1.0.0",            # Marker (fallback)

    # Knowledge Store
    "chromadb>=0.5.0",
    "networkx>=3.3",

    # Web UI
    "gradio>=5.0.0",
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",

    # Utilities
    "pydantic-settings>=2.5.0",
    "structlog>=24.0.0",
    "jinja2>=3.1.0",
    "python-dotenv>=1.0.0",

    # Database
    "psycopg[binary]>=3.2.0",       # PostgreSQL for checkpointing
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "ruff>=0.7.0",
]
```

---

## 9. 품질 보증 & 평가 전략

### 9.1 자동화 테스트

| 레벨 | 대상 | 도구 | 기준 |
|------|------|------|------|
| Unit | 각 Tool 함수 (arXiv, S2, writer) | pytest + mock | 100% 커버리지 |
| Integration | 에이전트 노드 단위 (입출력 계약) | pytest + fixture | 상태 스키마 준수 확인 |
| E2E | 전체 파이프라인 | LangSmith Tracing | 응답 시간 < 5분, 에러율 < 5% |

### 9.2 지식 품질 평가 메트릭

| 메트릭 | 측정 방법 | 목표치 |
|--------|----------|--------|
| **Grounding Accuracy** | 생성된 claim 중 원본 PDF에 근거가 있는 비율 | ≥ 90% |
| **LaTeX Preservation** | 원본 수식 대비 파싱 후 정확도 | ≥ 95% |
| **Coverage** | 사용자 질문 대비 생성된 위키의 답변 범위 | research_questions의 ≥ 80% 커버 |
| **Consistency** | 위키 파일 간 수치/주장의 모순 건수 | 0건 (review 루프 후) |
| **Link Density** | 위키 파일 당 평균 백링크 수 | ≥ 3개 |

---

## 10. 확장 로드맵 (Phase 6+)

| 단계 | 기능 | 설명 |
|------|------|------|
| **v1.1** | 시각적 추론 통합 | 논문 내 그림/도표를 Gemini Vision으로 분석, 자동 캡션 생성 및 지식 노드에 통합 |
| **v1.2** | 실시간 논문 모니터링 | arXiv RSS + cron → 새 논문 발견 시 자동 분석 파이프라인 트리거 |
| **v1.3** | 협업 모드 | 다중 사용자가 동일 vault에 접근, 충돌 해결 메커니즘 (CRDTs) |
| **v1.4** | 논문 작성 보조 | 축적된 지식 그래프를 기반으로 Related Work 섹션 초안 자동 생성 |
| **v1.5** | 로컬 LLM 옵션 | Gemma 4 또는 Llama 4를 Ollama로 실행하여 완전 오프라인 동작 |
| **v2.0** | 프로덕션 배포 | Neo4j 전환, Docker Compose, Firebase Hosting, CI/CD 파이프라인 |

---

## 참고 문헌 매핑

> 본 문서의 설계는 `research.md`와 `uix.md`의 모든 참고 문헌 [1]~[33]을 커버합니다.

| 설계 영역 | 매핑된 참고 문헌 |
|-----------|----------------|
| Long-Context Synthesis | [1], [2] |
| Planning-Analysis-Generation | [1], [3] |
| 자동화 문헌 리뷰 | [4], [5] |
| Ablation 지식 추출 | [6], [7] |
| 신뢰성 검증 (Linting) | [8], [9] |
| 시각적 추론 | [10], [11] |
| LangGraph 오케스트레이션 | [12], [13], [18] |
| Outline Agent | [14], [15] |
| 논문 검색·검증 | [4], [16] |
| Obsidian 위키 생성 | [17] |
| PDF 파싱 (라텍 보존) | [11], [19] |
| Mermaid 시각화 | [20], [21] |
| Idea Thrower 입력 | [22] |
| 계획 수립 | [23], [24] |
| 지식 조립 루프 | [25], [26] |
| AI-First, Local-First | [27], [28] |
| Agent Action Log | [29], [30] |
| Verification Overlay | [8], [31] |
| LaTeX 환경 | [11], [32] |
| Offline Readiness | [28], [33] |
