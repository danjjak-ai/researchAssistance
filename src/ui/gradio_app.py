import gradio as gr
from src.ui.components.idea_thrower import create_idea_thrower
from src.ui.components.knowledge_canvas import create_knowledge_canvas, MERMAID_JS
from src.ui.components.action_log import create_action_log
from src.agents.graph import app as research_app
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
                mermaid_html, node_detail = create_knowledge_canvas()

        # 에이전트 실행 로직
        def execute_research(query, files, history):
            logger.info("ui_research_started", query=query)
            
            initial_state = {
                "user_query": query,
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
            except Exception as e:
                logger.error("ui_run_failed", error=str(e))
                history.append({"role": "assistant", "content": f"❌ 오류 발생: {str(e)}"})
                yield history, "⚠️ 연구 중단", gr.update()

        submit_btn.click(
            execute_research,
            inputs=[query_input, file_input, log_display],
            outputs=[log_display, status_bar, mermaid_html]
        )
        
        demo.load(None, None, None, js=MERMAID_JS)

    return demo

if __name__ == "__main__":
    ui = create_ui()
    ui.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
