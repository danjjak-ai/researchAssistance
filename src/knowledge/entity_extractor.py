from typing import List, Dict
import json
from src.core.llm import get_llm
from src.core.logger import logger

def extract_entities_and_relations(text: str) -> Dict:
    """텍스트에서 엔티티와 관계를 추출합니다 (graphify 스타일의 신뢰도 태깅 적용)."""
    llm = get_llm()
    
    prompt = f"""
    당신은 고급 지식 그래프 구축 전문가입니다. 다음 텍스트에서 주요 개념(엔티티)과 이들 사이의 관계를 추출하세요.
    단순한 사실 추출을 넘어, 관계의 성격과 신뢰도를 명확히 구분해야 합니다.

    텍스트:
    {text}
    
    추출 지침:
    1. 엔티티: 개념, 방법론, 데이터셋, 지표 등을 핵심 키워드로 추출하세요.
    2. 관계: 소스 엔티티와 타겟 엔티티 사이의 연결을 정의하세요.
    3. 신뢰도 태그 (tag):
       - EXTRACTED: 텍스트에 직접적으로 명시된 사실.
       - INFERRED: 텍스트를 바탕으로 논리적으로 추론 가능한 관계 (높은 확신).
       - AMBIGUOUS: 관계가 암시적이지만 해석의 여지가 있거나 검토가 필요한 경우.
    4. 근거 (rationale): 왜 해당 관계가 성립하는지 텍스트 내용을 바탕으로 짧게 설명하세요.

    응답은 반드시 다음 JSON 형식을 유지하세요:
    {{
        "entities": [
            {{ "id": "개념명", "type": "Concept/Method/Dataset", "description": "설명" }}
        ],
        "relationships": [
            {{ 
                "source": "A", 
                "target": "B", 
                "type": "상세 관계 종류", 
                "tag": "EXTRACTED/INFERRED/AMBIGUOUS",
                "confidence": 0.0-1.0,
                "rationale": "추출 또는 추론의 근거"
            }}
        ]
    }}
    JSON 형식만 응답하고 다른 텍스트는 포함하지 마세요.
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
