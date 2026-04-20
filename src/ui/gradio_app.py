import os
import base64
import gradio as gr
from src.ui.components.idea_thrower import create_idea_thrower
from src.ui.components.knowledge_canvas import create_knowledge_canvas, MERMAID_JS
from src.ui.components.action_log import create_action_log
from src.agents.graph import app as research_app
from src.agents.outline_agent import QuotaExhaustedError
from src.core.logger import logger

def create_ui():
    with gr.Blocks(title="Agentic Research Assistant") as demo:
        gr.Markdown("# 🔬 Research Knowledge Compiler")
        gr.Markdown("에이전트가 논문을 분석하고 Obsidian에 지식을 구축합니다.")
        
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
                yield history, "⚠️ 입력 필요", gr.update()
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
                "mermaid_code": "graph TD\nPlanning[연구 계획 중...]",
                "review_issues": [],
                "verification_pairs": [],
                "messages": [],
                "iteration_count": 0,
                "max_iterations": 3,
                "status": "planning"
            }
            
            history = history or []
            yield history, "🔄 연구 계획 수립 중...", gr.update()

            try:
                # LangGraph 스트리밍
                for event in research_app.stream(initial_state, config={"configurable": {"thread_id": "ui_run"}}):
                    for node_name, state in event.items():
                        msg = f"✅ 에이전트 완료: {node_name}"
                        history.append({"role": "assistant", "content": msg})
                        
                        # 논문 검색 결과 표시 추가
                        if node_name == "search" and state.get("verified_papers"):
                            papers = state["verified_papers"]
                            paper_list = "### 📚 arXiv 검색 결과:\n"
                            for p in papers:
                                paper_list += f"- **{p['title']}** ({p['year']})  \n  [PDF 보기]({p['pdf_url']}) | 인용수: {p.get('citation_count', 0)}\n"
                            history.append({"role": "assistant", "content": paper_list})
                        
                        # Mermaid 업데이트 체크
                        current_mermaid = state.get("mermaid_code", "")
                        mermaid_val = f'<div class="mermaid">{current_mermaid}</div>' if current_mermaid else gr.update()
                        
                        yield history, f"⏳ {node_name} 실행 중...", mermaid_val
                
                history.append({"role": "assistant", "content": "🎉 연구 분석이 완료되었습니다!"})
                
                # 리포트 데이터 로드 및 반영
                audit_content = "### 📊 Graph Audit Report\n리포트를 불러오는 중입니다..."
                final_state = state # 마지막 상태
                
                if final_state.get("audit_report_path") and os.path.exists(final_state["audit_report_path"]):
                    with open(final_state["audit_report_path"], "r", encoding="utf-8") as f:
                        audit_content = f.read()
                
                # 인터랙티브 HTML 로드 (iframe 대응)
                interactive_val = gr.update()
                if final_state.get("graph_report_path") and os.path.exists(final_state["graph_report_path"]):
                    with open(final_state["graph_report_path"], "r", encoding="utf-8") as f:
                        html_content = f.read()
                        # Base64 인코딩하여 iframe에 삽입
                        import base64
                        b64_html = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
                        interactive_val = f'<iframe src="data:text/html;base64,{b64_html}" style="width:100%; height:600px; border:none; border-radius:8px;"></iframe>'

                yield history, "✅ 연구 완료", gr.update(), interactive_val, audit_content
                        
            except QuotaExhaustedError as e:
                logger.error("ui_quota_exhausted", error=str(e))
                error_msg = (
                    "❌ **API 쿼터 소진**\n\n"
                    "Google Gemini API의 무료 사용 한도를 초과했습니다.\n\n"
                    "**해결 방법:**\n"
                    "1. [Google AI Studio](https://aistudio.google.com/apikey)에서 새 API 키 발급\n"
                    "2. `.env` 파일의 `GOOGLE_API_KEY`를 새 키로 교체\n"
                    "3. 앱 재시작\n\n"
                    "또는 무료 쿼터가 리셋될 때까지 기다려주세요 (보통 24시간)."
                )
                history.append({"role": "assistant", "content": error_msg})
                yield history, "⚠️ API 쿼터 소진 — API 키를 확인하세요", gr.update()
            except Exception as e:
                logger.error("ui_run_failed", error=str(e))
                error_str = str(e)
                
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    error_msg = (
                        "❌ **API 요청 한도 초과 (429)**\n\n"
                        "잠시 후 다시 시도하거나, `.env`에서 API 키를 갱신하세요."
                    )
                elif "401" in error_str or "UNAUTHENTICATED" in error_str:
                    error_msg = "❌ **인증 실패**: `.env` 파일의 `GOOGLE_API_KEY`가 올바르지 않습니다."
                elif "404" in error_str or "NOT_FOUND" in error_str:
                    error_msg = (
                        "❌ **모델을 찾을 수 없음**\n\n"
                        "`.env`의 모델명을 확인하세요. 유효한 예: `gemini-2.5-flash-preview-04-17`"
                    )
                else:
                    error_msg = f"❌ 오류 발생: {error_str}"
                
                history.append({"role": "assistant", "content": error_msg})
                yield history, "⚠️ 연구 중단", gr.update()

        submit_btn.click(
            execute_research,
            inputs=[query_input, file_input, log_display],
            outputs=[log_display, status_bar, mermaid_html, interactive_html, node_detail]
        )
        
        # 새 창에서 열기 버튼 로직 (HTML 다운로드 링크처럼 동작하게 함)
        def open_report(history):
            # 실제로는 파일 경로를 반환하거나 gr.File을 사용하여 다운로드하게 할 수 있음
            return gr.update()

        open_btn.click(fn=lambda: None, js='() => window.open("/file=vault/output/graph.html", "_blank")')
        
        demo.load(None, None, None, js=MERMAID_JS)

    return demo

if __name__ == "__main__":
    ui, theme = create_ui()
    ui.launch(server_name="0.0.0.0", server_port=7860, share=False, theme=theme)
