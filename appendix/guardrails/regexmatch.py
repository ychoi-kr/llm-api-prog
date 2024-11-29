from guardrails import Guard, OnFailAction
from guardrails.hub import RegexMatch

guard = Guard().use(
    RegexMatch, regex=r"\(?\d{3}\)?-? *\d{3}-? *-?\d{4}", on_fail=OnFailAction.EXCEPTION
)

# 가드레일을 사용하여 텍스트 유효성 검사
valid_phone_number = "031-955-3658"
invalid_phone_number = "031-95-3658"

for phone_number in [valid_phone_number, invalid_phone_number]:
    try:
        guard.validate(phone_number)
        print(f"{phone_number}은 유효한 전화번호입니다.")
    except Exception as e:
        print(f"{phone_number}은 유효하지 않은 전화번호입니다.")
