# 🔬 Research Knowledge Compiler

> **エージェンティックな知識構造化とLong-Context合成による研究支援システム**

研究者の短いアイデアやログを基に、AIエージェントが自律的に論文を検索・分析・合成し、Obsidian形式のローカル知識ウィキを構築するプロジェクトです。

## ✨ 主な機能

- **エージェンティック・ワークフロー**: LangGraphに基づいた循環型マルチエージェント・アーキテクチャ (Outline → Search → Synthesis → Wiki → Review)。
- **Long-Context合成**: Gemini 3.1 Proの200万トークン・コンテキスト窓を活用し、複数の論文全文を一度に統合分析。
- **GraphRAGによる構造化**: 単純な検索を超え、エンティティ・リレーション抽出による知識グラフの構築と可視化を実現。
- **Obsidianネイティブ**: 全ての結果はバックリンクとタグを含むMarkdownファイルとして生成され、Obsidianですぐに活用可能。
- **自己修正ロジック**: Reviewエージェントが生成された知識の論理的矛盾や数値の不一致を検出し、修正ループを実行。

## 🛠️ 技術スタック

- **オーケストレーション**: LangGraph
- **LLM**: Gemini 3.1 Pro (Primary), Gemini 3.1 Flash (Fast)
- **PDF解析**: MinerU, Marker
- **知識ストア**: NetworkX, ChromaDB
- **Web UI**: Gradio

## 📁 プロジェクト構造

```
research-assistant/
├── src/
│   ├── agents/      # LangGraphエージェント (Outline, Search, Synthesis など)
│   ├── tools/       # 外部API & ファイル処理ツール (arXiv, S2, Obsidian)
│   ├── ui/          # GradioベースのWebダッシュボード
│   ├── knowledge/   # 知識グラフ & エンティティ抽出ロジック
│   └── core/        # 共通設定 & ロガー
├── vault/           # Obsidian互換の出力ディレクトリ (PDF原本, Wiki MD)
└── pyproject.toml   # uvパッケージ管理設定
```

## 🚀 はじめに

### 1. 前提条件
- [uv](https://github.com/astral-sh/uv) パッケージマネージャーのインストール
- Google AI Studio (Gemini) APIキーが必要

### 2. インストールと設定
```bash
# 依存関係のインストール
uv sync

# 環境変数の設定
cp .env.example .env
# .envファイルを開き、GOOGLE_API_KEYなどの設定を入力してください。
```

### 3. Web UIの実行
```bash
python -m src.ui.gradio_app
```
ブラウザで `http://localhost:7860` にアクセスし、研究アイデアを入力してください。

## 📖 参考ドキュメント
- [plan.md](./plan.md): 詳細な実装マスタープランとアーキテクチャ
- [research.md](./research.md): 知識構造化の理論的背景
- [uix.md](./uix.md): UI/UXデザインの原則

## 📄 ライセンス
MIT License
