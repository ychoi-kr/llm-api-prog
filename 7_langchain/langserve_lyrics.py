from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langserve import add_routes

# FastAPI 앱 초기화
app = FastAPI()

# OpenAI 모델 설정
openai_model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=1.2
)

# 프롬프트 템플릿 생성
prompt = ChatPromptTemplate.from_template("{topic}에 관해 노랫말을 써줘.")

# 모델과 프롬프트를 체인으로 묶기
chain = prompt | openai_model

# 경로를 앱에 추가
add_routes(app, chain, path="/lyrics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
