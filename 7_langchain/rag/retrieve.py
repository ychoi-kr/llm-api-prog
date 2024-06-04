from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

hf_model = HuggingFaceEmbeddings(model_name='jhgan/ko-sroberta-multitask')
vector_store = Chroma(persist_directory="./database", embedding_function=hf_model)
retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={'k': 5, 'fetch_k': 10})

template = """
[context]: {context}
```
[질의]: {query}
```
[예시]
신용 환산율입니다.
```
위의 [context] 정보 내에서 [질의]에 대해 답변 [예시]와 같이 술어를 붙여서 답하세요.
"""
prompt = ChatPromptTemplate.from_template(template)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)

def merge_pages(pages):
    merged = "\n\n".join(page.page_content for page in pages)
    print(f"참조 문서 시작==>[\n{merged}\n]<==참조 문서 끝")
    return merged

chain = (
    {"query": RunnablePassthrough(), "context": retriever | merge_pages}
    | prompt
    | llm
    | StrOutputParser()
)

answer = chain.invoke("짧은 기간 동안의 차익을 위해 금융사가 보유하는 걸 뜻하는 용어가 뭐야?")
print(f"answer1: {answer}\n\n")

answer = chain.invoke("트레이딩 포지션이 뭐야?")
print(f"answer2: {answer}")
