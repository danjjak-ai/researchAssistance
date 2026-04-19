# 🔬 Research Knowledge Compiler

> **에이전틱 지식 구조화 및 Long-Context 합성을 통한 연구 보조 시스템**

연구자의 짧은 아이디어나 로그를 바탕으로 AI 에이전트들이 자율적으로 논문을 검색, 분석, 합성하여 Obsidian 방식의 로컬 지식 위키를 구축해주는 프로젝트입니다.

## ✨ 주요 특징

- **Agentic Workflow**: LangGraph 기반의 순환형 멀티 에이전트 아키텍처 (Outline → Search → Synthesis → Wiki → Review).
- **Long-Context Synthesis**: Gemini 3.1 Pro의 200만 토큰 컨텍스트를 활용하여 다수의 논문 전문(full-text)을 한 번에 통합 분석.
- **GraphRAG 지식 구조화**: 단순 검색을 넘어 엔티티-관계 추출을 통한 지식 그래프 구축 및 시각화.
- **Obsidian Native**: 모든 결과물은 백링크와 태그가 포함된 마크다운 파일로 생성되어 Obsidian에서 즉시 활용 가능.
- **Self-Correction Logic**: Review 에이전트가 생성된 지식의 논리적 모순과 수치 불일치를 검토하고 재수정 루프 수행.

## 🛠️ 기술 스택

- **Orchestration**: LangGraph
- **LLM**: Gemini 3.1 Pro (Primary), Gemini 3.1 Flash (Fast)
- **PDF Parsing**: MinerU, Marker
- **Knowledge Store**: NetworkX, ChromaDB
- **Web UI**: Gradio

## 📁 프로젝트 구조

```
research-assistant/
├── src/
│   ├── agents/      # LangGraph 에이전트 (Outline, Search, Synthesis 등)
│   ├── tools/       # 외부 API 및 파일 처리 도구 (arXiv, S2, Obsidian)
│   ├── ui/          # Gradio 기반 웹 대시보드
│   ├── knowledge/   # 지식 그래프 및 엔티티 추출 로직
│   └── core/        # 공통 설정 및 로거
├── vault/           # Obsidian 호환 출력 디렉터리 (raw PDF, wiki MD)
└── pyproject.toml   # uv 패키지 관리 설정
```

## 🚀 시작하기

### 1. 전제 조건
- [uv](https://github.com/astral-sh/uv) 패키지 매니저 설치
- Google AI Studio (Gemini) API 키 필요

### 2. 설치 및 설정
```bash
# 의존성 설치
uv sync

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 GOOGLE_API_KEY와 기타 설정을 입력하세요.
```

### 3. 웹 UI 실행
```bash
python -m src.ui.gradio_app
```
브라우저에서 `http://localhost:7860`에 접속하여 아이디어를 입력하세요.

## 📖 참고 문서
- [plan.md](./plan.md): 상세 구현 마스터플랜 및 아키텍처
- [research.md](./research.md): 에이전틱 지식 구조화 이론적 배경
- [uix.md](./uix.md): 사용자 인터페이스 및 경험 설계 원칙

## 📄 라이선스
MIT License
