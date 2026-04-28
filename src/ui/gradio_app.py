import os
import base64
import gradio as gr
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import time

from src.ui.components.idea_thrower import create_idea_thrower
from src.ui.components.knowledge_canvas import create_knowledge_canvas, MERMAID_JS
from src.ui.components.action_log import create_action_log
from src.agents.graph import app as research_app
from src.core.llm import QuotaExhaustedError
from src.core.logger import logger

def create_ui():
    # Define a custom theme using only natively supported parameters
    # This prevents TypeError: Base.set() got an unexpected keyword argument 'primary_bg_fill'
    professional_theme = gr.themes.Soft(
        primary_hue="green",
        secondary_hue="slate",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
    )

    # Use custom CSS for branding and fine-tuned UI elements
    custom_css = """
    .gradio-container {
        background-color: #F8FAFC !important;
    }
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .stlyed-block {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        padding: 20px !important;
    }
    #mermaid-canvas, #interactive-canvas {
        min-height: 400px;
        background: #0F172A !important;
        border-radius: 8px;
    }
    """

    with gr.Blocks(title="Agentic Research Assistant", theme=professional_theme, css=custom_css) as demo:
        gr.Markdown("# 🔍 Research Knowledge Compiler", elem_id="main-title")
        gr.Markdown("에이전트가 논문을 분석하고 고도화된 지식 그래프를 구축합니다.")

        with gr.Row():
            with gr.Column(scale=1):
                query_input, file_input, submit_btn = create_idea_thrower()
                log_display, status_bar = create_action_log()

            with gr.Column(scale=2):
                mermaid_html, interactive_html, open_btn, node_detail = create_knowledge_canvas()

        # 에이전트 실행 로직
        def execute_research(query, files, history):
            if not query and not files:
                history = history or []
                history.append({"role": "assistant", "content": "⚠️ 연구 주제를 입력하거나 PDF 파일을 업로드해주세요."})
                yield history, "⚠️ 입력 필요", gr.update(), gr.update(), gr.update()
                return

            logger.info("ui_research_started", query=query)

            initial_state = {
                "user_query": query or "업로드된 PDF 파일 분석",
                "research_questions": [],
                "candidate_papers": [],
                "verified_papers": [],
                "pdf_paths": [f.name for f in files] if files else [],
                "parsed_markdowns": [],
                "synthesis_notes": [],
                "ablation_findings": [],
                "knowledge_graph": {"nodes": [], "edges": []},
                "wiki_files": [],
                "mermaid_code": "graph TD\nPlanning[연구 계획 수립 중...]",
                "review_issues": [],
                "verification_pairs": [],
                "messages": [],
                "iteration_count": 0,
                "max_iterations": 3,
                "status": "planning"
            }

            history = history or []
            yield history, "⚙️ 연구 계획 수립 중...", gr.update(), gr.update(), gr.update()

            try:
                # LangGraph 스트리밍
                state = initial_state
                for event in research_app.stream(initial_state, config={"configurable": {"thread_id": "ui_run"}}):
                    for node_name, node_state in event.items():
                        state.update(node_state)
                        msg = f"✦ 단계 완료: **{node_name}**"
                        history.append({"role": "assistant", "content": msg})

                        # 논문 검색 결과 표시
                        if node_name == "search" and state.get("verified_papers"):
                            papers = state["verified_papers"]
                            paper_list = "### 📚 확인된 논문:\n"
                            for p in papers:
                                paper_list += f"- **{p['title']}** ({p['year']})  \n  [PDF]({p['pdf_url']})\n"
                            history.append({"role": "assistant", "content": paper_list})

                        # Mermaid 실시간 업데이트
                        current_mermaid = state.get("mermaid_code", "")
                        mermaid_val = f'<div class="mermaid">{current_mermaid}</div>' if current_mermaid else gr.update()

                        yield history, f"⟳ {node_name} 수행 중...", mermaid_val, gr.update(), gr.update()

                history.append({"role": "assistant", "content": "🎉 **연구 분석이 모두 완료되었습니다!**"})

                # 결과 데이터 시각화
                audit_content = "### 📊 분석 보고서 생성 실패"
                if state.get("audit_report_path") and os.path.exists(state["audit_report_path"]):
                    with open(state["audit_report_path"], "r", encoding="utf-8") as f:
                        audit_content = f.read()

                # 인터랙티브 그래프 임베딩 (FastAPI 정적 경로 사용)
                interactive_val = gr.update()
                if state.get("graph_report_path") and os.path.exists(state["graph_report_path"]):
                    interactive_val = f'<iframe src="/static/vault/output/graph.html?t={int(time.time())}" style="width:100%; height:600px; border:none; border-radius:12px;"></iframe>'

                yield history, "✅ 분석 성공", gr.update(), interactive_val, audit_content

            except QuotaExhaustedError as e:
                history.append({"role": "assistant", "content": f"❌ **API 사용량 초과 (해결 방법)**:\n\n무료 사용량이 소진되었거나 서버 트래픽이 초과되었습니다.\n\n{str(e)}"})
                yield history, "⚠️ 사용량 초과", gr.update(), gr.update(), gr.update()
            except Exception as e:
                logger.error("ui_run_failed", error=str(e))
                error_str = str(e)
                if "503" in error_str or "UNAVAILABLE" in error_str:
                    error_msg = "❌ **API 서버 혼잡 (503)**\n\nGoogle Gemini 서버의 트래픽이 급증하여 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
                elif "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    error_msg = "❌ **API 요청 한도 초과 (429)**\n\n잠시 후 다시 시도하거나, `.env`에서 API 키를 갱신하세요."
                elif "401" in error_str or "UNAUTHENTICATED" in error_str:
                    error_msg = "❌ **인증 실패 (401)**\n\n`.env` 파일의 `GOOGLE_API_KEY`가 올바른지 확인하세요."
                elif "404" in error_str or "NOT_FOUND" in error_str:
                    error_msg = "❌ **모델을 찾을 수 없음 (404)**\n\n`.env`의 모델명을 확인하세요. (예: `gemini-2.5-flash`)"
                else:
                    error_msg = f"❌ **오류 발생**: {error_str}"
                
                history.append({"role": "assistant", "content": error_msg})
                yield history, "⚠️ 에러 발생", gr.update(), gr.update(), gr.update()

        submit_btn.click(
            execute_research,
            inputs=[query_input, file_input, log_display],
            outputs=[log_display, status_bar, mermaid_html, interactive_html, node_detail]
        )

        def get_graph_file_url():
            return f"/static/vault/output/graph.html?t={int(time.time())}"

        open_btn.click(fn=None, js=f'() => window.open("{get_graph_file_url()}", "_blank")')
        demo.load(None, None, None, js=MERMAID_JS)

    return demo

if __name__ == "__main__":
    demo = create_ui()
    app = FastAPI()
    
    # vault 디렉토리를 /static/vault 경로로 직접 서빙 (윈도우 경로 문제 해결)
    vault_abs_path = os.path.abspath("vault")
    app.mount("/static/vault", StaticFiles(directory=vault_abs_path), name="vault")
    
    # Gradio 앱 마운트
    gr.mount_gradio_app(app, demo, path="/")
    
    print(f"[INFO] FastApi + Gradio Server starting on http://localhost:7860")
    uvicorn.run(app, host="0.0.0.0", port=7860)
