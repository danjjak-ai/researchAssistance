from pathlib import Path
from datetime import date
from langchain_core.tools import tool
from src.config import settings
from src.core.logger import logger

@tool
def write_wiki_file(
    filename: str,
    content: str,
    tags: list[str],
    sources: list[str],
    related: list[str],
) -> str:
    """Obsidian 호환 마크다운 파일을 vault/wiki에 생성합니다."""
    wiki_dir = settings.WIKI_DIR
    wiki_dir.mkdir(parents=True, exist_ok=True)
    
    frontmatter = f"""---
tags: {tags}
created: {date.today().isoformat()}
sources: {sources}
related: {[f'[[{r}]]' for r in related]}
---
"""
    # Filename cleanup
    safe_filename = filename.replace(" ", "_").replace("/", "_")
    filepath = wiki_dir / f"{safe_filename}.md"
    
    try:
        filepath.write_text(frontmatter + content, encoding="utf-8")
        _update_index(safe_filename, tags)
        logger.info("wiki_file_written", path=str(filepath))
        return f"✅ {filepath} 생성 완료"
    except Exception as e:
        logger.error("wiki_write_failed", filename=filename, error=str(e))
        return f"❌ {filename} 생성 실패: {str(e)}"

def _update_index(filename: str, tags: list[str]):
    index_path = settings.VAULT_DIR / "_index.md"
    entry = f"- [[{filename}]] — {', '.join(tags)}\n"
    try:
        with open(index_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        logger.error("index_update_failed", error=str(e))
