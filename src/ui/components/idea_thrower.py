import gradio as gr

def create_idea_thrower():
    with gr.Column(scale=1, variant="panel"):
        gr.Markdown("### 💡 Idea Thrower")
        query_input = gr.Textbox(
            placeholder="연구 주제를 입력하거나 파일을 업로드하세요...",
            lines=4,
            label=None,
            show_label=False
        )
        file_input = gr.File(
            label="PDF/Markdown 파일 업로드",
            file_types=[".pdf", ".md"],
            file_count="multiple"
        )
        submit_btn = gr.Button("연구 시작 🚀", variant="primary")
    return query_input, file_input, submit_btn
