# 🔬 Research Knowledge Compiler

> **Agentic Knowledge Structuring & Long-Context Synthesis Research Assistant**

An autonomous multi-agent system that helps researchers search, analyze, and synthesize papers based on short ideas or logs, building a local knowledge wiki in Obsidian format.

## ✨ Key Features

- **Agentic Workflow**: Cyclic multi-agent architecture based on LangGraph (Outline → Search → Synthesis → Wiki → Review).
- **Long-Context Synthesis**: Leverages Gemini 3.1 Pro's 2M token context window to analyze multiple full-text papers simultaneously.
- **GraphRAG-inspired Structuring**: Go beyond simple search with entity-relation extraction for knowledge graph construction and visualization.
- **Obsidian Native**: Outputs are generated as Markdown files with backlinks and tags, ready for use in Obsidian.
- **Self-Correction Logic**: A specialized Review agent detects logical contradictions or numerical inconsistencies and triggers a correction loop.

## 🛠️ Technology Stack

- **Orchestration**: LangGraph
- **LLM**: Gemini 3.1 Pro (Primary), Gemini 3.1 Flash (Fast)
- **PDF Parsing**: MinerU, Marker
- **Knowledge Store**: NetworkX, ChromaDB
- **Web UI**: Gradio

## 📁 Project Structure

```
research-assistant/
├── src/
│   ├── agents/      # LangGraph agents (Outline, Search, Synthesis, etc.)
│   ├── tools/       # External APIs & file processing (arXiv, S2, Obsidian)
│   ├── ui/          # Gradio-based web dashboard
│   ├── knowledge/   # Knowledge graph & entity extraction logic
│   └── core/        # Common config & logger
├── vault/           # Obsidian-compatible output (raw PDFs, wiki MDs)
└── pyproject.toml   # uv dependency management
```

## 🚀 Getting Started

### 1. Prerequisites
- [uv](https://github.com/astral-sh/uv) package manager
- Google AI Studio (Gemini) API Key

### 2. Installation & Setup
```bash
# Install dependencies
uv sync

# Setup environment variables
cp .env.example .env
# Open .env and fill in your GOOGLE_API_KEY and other settings.
```

### 3. Run Web UI
```bash
python -m src.ui.gradio_app
```
Access `http://localhost:7860` in your browser and start typing your research ideas.

## 📖 Documentation
- [plan.md](./plan.md): Detailed implementation master plan & architecture
- [research.md](./research.md): Theoretical background on agentic knowledge structuring
- [uix.md](./uix.md): UI/UX design principles

## 📄 License
MIT License
