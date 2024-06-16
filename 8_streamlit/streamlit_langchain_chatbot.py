from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

import streamlit as st

st.title("스트림릿 랭체인 챗봇 예제")

# 메모리 설정
msgs = StreamlitChatMessageHistory()
if len(msgs.messages) == 0:
    msgs.add_ai_message("안녕하세요?")

# 메시지 히스토리를 전달해 랭체인을 설정

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI chatbot having a conversation with a human."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=st.secrets["OPENAI_API_KEY"]
)

chain = prompt | llm
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
)

# StreamlitChatMessageHistory에서 현재 메시지 렌더링
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# 사용자가 새 프롬프트를 입력하면 새 응답을 생성하고 그리기
if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    # 새 메시지는 실행 중 랭체인에 의해 자동으로 기록됨
    config = {"configurable": {"session_id": "any"}}
    response = chain_with_history.invoke({"question": prompt}, config)
    st.chat_message("ai").write(response.content)
