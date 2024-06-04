# 다음 영상의 코드를 수정함.
# Stream LLMs with LangChain + Streamlit | Tutorial
# https://www.youtube.com/watch?v=zKGeRWjJlTU

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.set_page_config(page_title="Streaming Bot", page_icon="🤖")

st.title("Streaming Bot")

def get_response(query, chat_history):
    template = """
        You are a helpful assistant. Answer the following questions considering the context of the conversation.
        
        Chat history: {chat_history}
        
        User question: {user_question}
        """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatOpenAI(
        model="gpt-4-turbo-preview",
        api_key=st.secrets["OPENAI_API_KEY"]
    )

    chain = prompt | llm | StrOutputParser()

    return chain.stream({
        "chat_history": chat_history,
        "user_question": query
    })
    
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)
    else:
        with st.chat_message("AI"):
            st.markdown(message.content)

user_query = st.chat_input("Your message")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        ai_response = st.write_stream(get_response(user_query, st.session_state.chat_history))

    st.session_state.chat_history.append(AIMessage(content=ai_response))