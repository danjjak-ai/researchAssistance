from typing import List, Dict
import json
from src.agents.outline_agent import get_llm
from src.core.logger import logger

def extract_entities_and_relations(text: str) -> Dict:
    """텍스트에서 엔티티와 관계를 추출합니다 (GraphRAG 아키텍처 반영)."""
    llm = get_llm()
    
    prompt = f"""
    당신은 지식 그래프 구축 전문가입니다. 다음 텍스트에서 주요 엔티티와 이들 사이의 관계를 추출하세요.
    
    텍스트:
    {text}
    
    다음 JSON 형식으로 응답하세요:
    {{
        "entities": [
            {{ "id": "Name", "type": "Concept/Method/Dataset/Metric", "description": "설명" }}
        ],
        "relationships": [
            {{ "source": "A", "target": "B", "type": "uses/extends/improves/contradicts", "description": "관계 설명" }}
        ]
    }}
    JSON 형식만 유지하세요.
    """
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        logger.error("entity_extraction_failed", error=str(e))
        return {"entities": [], "relationships": []}
