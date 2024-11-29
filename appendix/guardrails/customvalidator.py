import re
from rich import print

# 휴대폰 번호와 주민등록번호를 검출하는 간단한 개인 식별 정보(PII) 검출기
class SimplePIIValidator:
    def __init__(self):
        self.regex_patterns = {
            "휴대폰_번호": r"01[0-9]-\d{3,4}-\d{4}",
            "주민등록번호": r"[0-9]{6}-[1-4][0-9]{6}"
        }
    
    def detect_pii(self, text):
        detected_pii = []
        for entity, pattern in self.regex_patterns.items():
            matches = list(re.finditer(pattern, text))
            for match in matches:
                detected_pii.append({
                    "entity": entity,
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group()
                })
        return detected_pii

# Guardrails와 통합
def guardrails_with_simple_pii(text):
    validator = SimplePIIValidator()
    detected_pii = validator.detect_pii(text)
    
    # 시작 위치 역순으로 정렬하여 문자열 인덱스가 변경되지 않도록 함
    detected_pii.sort(key=lambda x: x['start'], reverse=True)
    
    # PII를 마스킹 처리
    for pii in detected_pii:
        text = text[:pii["start"]] + f"<{pii['entity']}>" + text[pii["end"]:]
    return text

# 테스트 텍스트
test_text = "제 주민등록번호는 900101-1234567이고, 전화번호는 010-1234-5678입니다."

# Guardrails를 사용한 처리
masked_output = guardrails_with_simple_pii(test_text)

# 결과 출력
print(masked_output)
