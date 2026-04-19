# UIX: 사용자 인터페이스 및 경험 설계

## 1. 디자인 원칙: "AI-First, Local-First"
사용자의 데이터가 로컬(Obsidian)에 남으면서도 AI가 이를 자유롭게 수정할 수 있는 환경을 제공합니다 [27, 28].

## 2. 주요 UI 컴포넌트
- **The Idea Thrower (Input Box)**: 화면 중앙에 위치한 단순한 입력창. 사용자는 짧은 단어나 연구 로그 파일을 드래그 앤 드롭하여 입력을 시작합니다 [22].
- **Knowledge Canvas (Mermaid.js Integration)**: AI가 현재 구축 중인 지식의 구조를 실시간 그래프로 보여줍니다. 노드를 클릭하면 해당 Obsidian 마크다운 파일이 열립니다 [20, 21].
- **Agent Action Log**: AI가 어떤 논문을 읽고 있고, 어떤 개념 노드를 새로 생성했는지 실시간으로 스트리밍합니다 [29, 30].
- **Verification Overlay**: AI가 생성한 지식에 대해 "근거 문구"를 원본 PDF와 대조하여 보여주는 검토 창입니다 [8, 31].

## 3. 핵심 사용자 여정(User Journey)
1.  **Input**: 사용자가 "Transformer의 어블레이션 연구들 정리해줘"라고 입력합니다.
2.  **Process**: AI가 자동으로 관련 논문을 검색(Semantic Scholar)하고 전문을 분석합니다 [4, 16].
3.  **Output**: Obsidian 내에 `Attention_Mechanism.md`, `Positional_Encoding.md` 등의 파일이 생성되고, 이들 간의 인과 관계가 백링크로 연결됩니다 [1, 17].
4.  **Review**: 사용자는 AI가 그린 Mermaid 그래프를 통해 전체 흐름을 한눈에 파악하고 필요한 부분을 수정합니다 [8, 20].

## 4. UX 차별점
- **Seamless LaTeX**: 연구원들이 선호하는 LaTeX 수식과 표(Table) 형식이 완벽하게 유지되는 Markdown 환경을 제공합니다 [11, 32].
- **Offline Readiness**: 한 번 분석된 지식은 로컬 마크다운 파일로 저장되어 인터넷 연결 없이도 조회가 가능합니다 [28, 33].
