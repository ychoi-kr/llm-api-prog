# 《OpenAI, 구글 Gemini, 업스테이지 Solar API를 활용한 실전 LLM 앱 개발》
**거대 언어 모델 API를 활용한 생성형 AI 애플리케이션 개발 가이드**

이 저장소는 《OpenAI, 구글 Gemini, 업스테이지 Solar API를 활용한 실전 LLM 앱 개발》 책의 예제 코드를 담고 있습니다. OpenAI, 구글 제미나이, 업스테이지 솔라 등 최신 LLM API를 활용해 실용적인 AI 애플리케이션을 개발하는 방법을 배울 수 있습니다.

## 실습 환경 요구사항

### 공통 요구사항
- Python 3.9 이상, 3.13 미만
- 구글 계정 (구글 드라이브와 코랩 사용)
- 신용카드/체크카드 (OpenAI, 구글, 업스테이지 API 서비스 이용료 결제)

### 로컬 PC 실습 환경 설정

```bash
# 저장소 복제
git clone https://github.com/ychoi-kr/llm-api-prog.git
cd llm-api-prog

# 가상환경 생성
python -m venv .venv

# 가상환경 활성화 (Windows)
.venv\Scripts\activate
# 가상환경 활성화 (macOS/Linux)
source .venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

## 주요 내용
- LLM API 통합과 활용 방법
- OpenAI 놀이터를 통한 LLM 기초
- 프롬프트 엔지니어링의 핵심 원리와 기법
- OpenAI, 구글 제미나이, 업스테이지 솔라 API 활용
- RAG를 활용한 지식 기반 AI 시스템 구축
- 랭체인과 플로와이즈를 활용한 애플리케이션 개발
- 스트림릿으로 구현하는 AI 웹 애플리케이션
- Flet으로 만드는 실시간 다국어 채팅 앱

## 실습 코드 구조

```
llm-api-prog/
├── 0_frontmatter/ - 앞부속
├── 4_openai/ - OpenAI API 실습
├── 5_gemini/ - 구글 제미나이 API 실습
├── 6_upstage/ - 업스테이지 솔라 API 실습
├── 7_langchain/ - 랭체인 실습
├── 8_streamlit/ - 스트림릿 애플리케이션
├── 9_flet/ - Flet 채팅 애플리케이션
├── data/ - 실습용 데이터
└── appendix/ - 부록
```
