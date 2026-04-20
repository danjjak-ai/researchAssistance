import gradio as gr

MERMAID_JS = """
async () => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js';
    document.head.appendChild(script);
    script.onload = () => {
        mermaid.initialize({ startOnLoad: true });
    };
}
"""

def create_knowledge_canvas():
    with gr.Column(scale=2, variant="panel"):
        gr.Markdown("### 🧠 Knowledge Canvas")
        
        with gr.Tabs():
            with gr.Tab("Static Graph (Mermaid)"):
                mermaid_html = gr.HTML(
                    value='<div class="mermaid">graph TD\nResearch[연구 주제를 입력하고 분석을 시작하세요]</div>',
                    elem_id="mermaid-canvas"
                )
            
            with gr.Tab("Interactive Graph (Graphify Style)"):
                gr.Markdown("심층 분석된 인터랙티브 지식 그래프입니다. (분석 완료 후 활성화)")
                interactive_html = gr.HTML(
                    value="<div style='background: #1e293b; padding: 40px; text-align: center; border-radius: 8px;'>분석이 완료되면 그래프 탐색기가 여기에 표시됩니다.</div>",
                    elem_id="interactive-canvas"
                )
                open_btn = gr.Button("🔗 새 창에서 지식 그래프 열기", variant="secondary")
        
        with gr.Accordion("지식 상세 및 감사 리포트", open=False):
            node_detail = gr.Markdown("감사 리포트와 상세 노드 정보가 여기에 표시됩니다.")
            
    return mermaid_html, interactive_html, open_btn, node_detail
