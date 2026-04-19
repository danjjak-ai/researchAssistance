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
        # Mermaid 렌더링을 위한 HTML 컨테이너
        mermaid_html = gr.HTML(
            value='<div class="mermaid">graph TD\nA-->B</div>',
            elem_id="mermaid-canvas"
        )
        with gr.Accordion("지식 상세", open=False):
            node_detail = gr.Markdown("노드를 선택하면 상세 내용이 표시됩니다.")
            
    return mermaid_html, node_detail
