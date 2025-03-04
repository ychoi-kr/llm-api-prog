# 《OpenAI, 구글 Gemini, 업스테이지 Solar API를 활용한 실전 LLM 앱 개발》
**프롬프트 작성부터 웹 앱 개발까지, 실습으로 배우는 LLM 서비스 개발**

이 저장소는 《OpenAI, 구글 Gemini, 업스테이지 Solar API를 활용한 실전 LLM 앱 개발》 책의 예제 코드를 담고 있습니다. OpenAI, 구글 제미나이, 업스테이지 솔라 등 최신 LLM API를 활용해 실용적인 AI 애플리케이션을 개발하는 방법을 배울 수 있습니다.

## 주요 내용
- LLM API 통합과 활용 방법
- OpenAI 플레이그라운드에서 LLM 기초 익히기
- 프롬프트 엔지니어링의 핵심 원리와 기법
- OpenAI, 구글 제미나이, 업스테이지 솔라 API 활용
- RAG를 활용한 지식 기반 AI 시스템 구축
- 랭체인과 플로와이즈를 활용한 애플리케이션 개발
- 스트림릿으로 구현하는 AI 웹 애플리케이션
- Flet으로 만드는 실시간 다국어 채팅 앱

## 실습 환경 요구사항 및 구성 방법

### 공통 요구사항
- Python 3.9 이상, 3.13 미만
- 구글 계정 (구글 드라이브와 코랩 사용)
- 신용카드/체크카드 (OpenAI, 구글, 업스테이지 API 서비스 이용료 결제)  
    API 가입과 키 발급 방법은 각 장에서 설명합니다.

### 구글 코랩 실습 환경 구성(4~7장)

1. [clone_repository.ipynb](https://colab.research.google.com/github/ychoi-kr/llm-api-prog/blob/main/0_frontmatter/clone_repository.ipynb) 노트북을 실행합니다.
2. 코랩 보안 비밀을 등록합니다.

자세한 설명은 앞 부속에 있는 ‘이 책의 사용 설명서’를 참조하세요.

### 로컬 PC 실습 환경 설정(7~9장)

#### 저장소 복제
```bash
git clone https://github.com/ychoi-kr/llm-api-prog.git
cd llm-api-prog
```

#### 가상환경 구성

가상환경을 만들어도 되고 가상환경 없이 실습해도 됩니다.

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화 (Windows)
.venv\Scripts\activate
# 가상환경 활성화 (macOS/Linux)
source .venv/bin/activate
```

아나콘다를 사용하는 경우 `conda` 명령을 사용해 가상환경을 생성해 실습해도 됩니다.

#### 패키지 설치

```bash
pip install -r requirements.txt
```

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

## 출간 이후 변경 사항 및 오탈자 수정

**17~28, 32페이지**  
OpenAI 플레이그라운드에서 Complete 메뉴가 삭제되었습니다.  
3월 15일까지는 웹브라우저에서 다음 주소를 직접 입력해 접근할 수 있습니다.  
[https://platform.openai.com/playground/complete?model=gpt-3.5-turbo-instruct](https://platform.openai.com/playground/complete?model=gpt-3.5-turbo-instruct)

**5장 및 7.7절**  
Gemini 2.0 Flash 모델을 사용하는 예제를 아래 주소에서 보실 수 있습니다.  
[Gemini 2.0 브랜치로 이동하기](https://github.com/ychoi-kr/llm-api-prog/tree/gemini-2.0)
