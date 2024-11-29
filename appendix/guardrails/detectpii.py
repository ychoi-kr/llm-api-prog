from guardrails.hub import DetectPII
import guardrails as gd
from rich import print

# 개인 식별 정보(PII) 검출기 생성
guard = gd.Guard().use(
    DetectPII(
        pii_entities="pii",
        on_fail="fix"  # 실패(PII 검출) 시 자동으로 마스킹 처리
    )
)

# 검출 대상 텍스트
text = """개인 정보입니다.
이름: 홍길동
이메일 주소: gdhong@wikibook.co.kr
전화번호: 010-1234-5678
주민등록번호: 900101-1234567
"""

# 검출 실행
output = guard.parse(
    llm_output=text,
    metadata={
        "pii_entities": [
            "EMAIL_ADDRESS", "PHONE_NUMBER"  # 이메일 주소와 전화번호 검출
        ]
    },
)

# 결과 출력
print(output)