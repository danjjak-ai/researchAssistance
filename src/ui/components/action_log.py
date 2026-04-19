import gradio as gr

def create_action_log():
    with gr.Column(scale=1, variant="panel"):
        gr.Markdown("### 🤖 Agent Action Log")
        log_display = gr.Chatbot(
            label=None,
            show_label=False,
            height=400
        )
        status_bar = gr.Markdown("⏳ 대기 중...")
    return log_display, status_bar
