import streamlit as st
from openai import OpenAI

st.title("시험 문제 생성기")

# Streamlit 시크릿에서 OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 지문 입력 받기
passage = st.text_area("지문을 입력하세요 (200자 내외):", height=200)

# 문항 유형 선택
question_type = st.radio("문항 유형을 선택하세요:", ("객관식", "주관식"))

if st.button("출제"):
    if passage.strip() == "":
        st.warning("지문을 입력해 주세요.")
    else:
        with st.spinner("문제를 생성하는 중..."):
            prompt = f"""
            다음 지문을 바탕으로 {'객관식' if question_type == '객관식' else '주관식'} 문제를 한 개 출제해 주세요.
            
            지문: {passage}
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )

            question = response.choices[0].message.content.strip()
            
        st.success("문제 생성 완료!")
        st.write(question)
        