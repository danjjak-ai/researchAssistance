---
name: ui-professional-redesign
description: Redesign of the Research Knowledge Compiler UI to a "Deep Neutral High-end" style.
type: design-spec
date: 2026-04-20
---

# UI Redesign Specification: Deep Neutral High-end

## 1. Objective
Transform the UI from a basic white background to a professional, academic-grade interface that reduces eye strain and communicates expertise and reliability.

## 2. Visual Identity
The "Deep Neutral High-end" style mimics a high-end research lab or a premium academic journal. It prioritizes readability, subtle contrast, and a sophisticated color palette.

### 2.1 Color Palette
| Element | Color Code | Description |
| :--- | :--- | :--- |
| **Main Background** | `#F5F5F4` | Very light warm grey for a paper-like feel |
| **Component Background** | `#FFFFFF` | Pure white for cards and input areas |
| **Primary Accent** | `#2D6A4F` | Deep Green for buttons, active states, and highlights |
| **Secondary Accent** | `#4A4E69` | Slate Grey for headers and secondary elements |
| **Primary Text** | `#1C1C1C` | Dark Grey for maximum readability |
| **Secondary Text** | `#6B7280` | Medium Grey for muted information |

### 2.2 Typography & Icons
- **Typography**: System Sans-serif with emphasized weights for headers to create a clear information hierarchy.
- **Icons**: Transition from generic emojis to minimal, line-based symbols.
  - Header: `🔬` $\rightarrow$ Professional Research Icon (SVG or refined symbol)
  - Search results: `📚` $\rightarrow$ Academic Library Icon
  - Status updates: `🔄`, `✅`, `⏳`, `❌` $\rightarrow$ Consistent, themed status indicators.

## 3. Implementation Details (Gradio)
- **Theme**: Replace `gr.themes.Soft()` with a custom `gr.Theme` configuration.
- **Custom CSS**: 
  - Apply `#F5F5F4` to the `.gradio-container` background.
  - Set primary button colors to `#2D6A4F`.
  - Refine border-radius for a more "architectural" and less "bubbly" look.
- **Components**:
  - `idea_thrower`: Refine input borders and button styles.
  - `action_log`: Use a cleaner, monospace font for logs with a subtle background.
  - `knowledge_canvas`: Ensure the Mermaid diagram colors complement the new palette.
