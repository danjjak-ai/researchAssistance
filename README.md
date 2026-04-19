# 🔬 Research Knowledge Compiler

[한국어](#korean) | [English](#english) | [日本語](#japanese)

---

<a name="korean"></a>
## 🇰🇷 Korean

> **에이전틱 지식 구조화 및 Long-Context 합성을 통한 연구 보조 시스템**

연구자의 짧은 아이디어나 로그를 바탕으로 AI 에이전트들이 자율적으로 논문을 검색, 분석, 합성하여 Obsidian 방식의 로컬 지식 위키를 구축해주는 프로젝트입니다.

### ✨ 주요 특징
- **Agentic Workflow**: LangGraph 기반의 순환형 멀티 에이전트 아키텍처.
- **Long-Context Synthesis**: Gemini 1.5 Pro의 컨텍스트를 활용한 통합 분석.
- **GraphRAG 지식 구조화**: 엔티티-관계 추출을 통한 지식 그래프 시각화.
- **Obsidian Native**: 백링크와 태그가 포함된 마크다운 파일 생성.

### 🚀 시작하기
```bash
uv sync
cp .env.example .env
python -m src.ui.gradio_app
```

---

<a name="english"></a>
## 🇺🇸 English

> **Agentic Knowledge Structuring & Long-Context Synthesis Research Assistant**

An autonomous multi-agent system that helps researchers search, analyze, and synthesize papers based on short ideas or logs, building a local knowledge wiki in Obsidian format.

### ✨ Key Features
- **Agentic Workflow**: Cyclic multi-agent architecture based on LangGraph.
- **Long-Context Synthesis**: Leverages Gemini 1.5 Pro's large context window.
- **GraphRAG-inspired Structuring**: Knowledge graph construction via entity-relation extraction.
- **Obsidian Native**: Outputs generated as tagged Markdown files.

### 🚀 Getting Started
```bash
uv sync
cp .env.example .env
python -m src.ui.gradio_app
```

---

<a name="japanese"></a>
## 🇯🇵 Japanese

> **エージェンティックな知識構造化とLong-Context合成による研究支援システム**

研究者の短いアイデアやログを基に、AIエージェントが自律的に論文を検索・分析・合成し、Obsidian形式のローカル知識ウィキを構築するプロジェクトです。

### ✨ 主な機能
- **エージェンティック・ワークフロー**: LangGraphに基づいた循環型マルチエージェント・アーキテクチャ。
- **Long-Context合成**: Gemini 1.5 Proを活用した複数論文の統合分析。
- **GraphRAGによる構造化**: エンティティ・リレーション抽出による知識グラフの可視化。
- **Obsidianネイティブ**: バック링크とタグを含むMarkdown生成。

### 🚀 はじめに
```bash
uv sync
cp .env.example .env
python -m src.ui.gradio_app
```

---

## 📄 License
MIT License
