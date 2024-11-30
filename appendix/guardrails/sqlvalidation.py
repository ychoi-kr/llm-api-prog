from guardrails import Guard
from guardrails.hub import ValidSQL
from rich import print

# ValidSQL 검사기로 Guard 생성 (DB나 스키마 없이 구문만 검증)
guard = Guard().use(
    ValidSQL,
    on_fail="exception"
)

# 검증할 SQL 문들
queries = [
    "SELECT 주소 FROM 전화번호부 WHERE 이름 = '도봉순';",
    "SELECT 이름, 휴대폰 FROM 전화번호부 WHERE 주소 LIKE '서울%';",
    "SELECT * FROM 전화번호부 WHERE ID = 2;",
    # 의도적으로 잘못된 SQL문 추가
    "SELEKT 주소 FRUM 전화번호부 WHER 이름 = '도봉순';"
]

# SQL 문 검증
def validate_sql(sql):
    try:
        guard.validate(sql)
        print(f"[green]✅ 성공: {sql}[/green]")
    except Exception:
        print(f"[red]❌ 실패: {sql}[/red]")

# 모든 쿼리 검증 실행
for query in queries:
    validate_sql(query)
