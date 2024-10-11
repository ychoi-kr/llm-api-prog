import streamlit as st
from openai import AsyncOpenAI, OpenAI
import asyncio
import pandas as pd
from io import BytesIO

default_model = "gpt-3.5-turbo"

st.set_page_config(layout="wide")

st.title("Multi-Model Sentence Corrector")
st.text(f"OpenAI의 기본 모델({default_model})과 사용자의 파인튜닝 모델을 사용해 문장을 교정합니다.")

async_client = AsyncOpenAI(api_key=st.secrets["OPENAI_API_KEY"])
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

col1, col2 = st.columns([0.3, 0.7])

async def correct(text, model, model_num):
    messages = [
        {"role": "system", "content": "다음 문장을 자연스러운 언어로 교정해 주세요."},
        {"role": "user", "content": text}
    ]
    response = await async_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0
    )
    corrected_text = response.choices[0].message.content.strip()
    model_alias = f"기본 모델" if model == default_model \
        else f"파인튜닝 모델 {model_num}" if model.startswith("ft:") \
        else f"사용자 지정 모델 {model_num}"
    st.session_state[model_alias] = corrected_text

async def main():
    if text.strip() == "":
        st.warning("문장을 입력해 주세요.")
    else:
        models = [default_model] + finetuned_models
        tasks = [asyncio.create_task(correct(text, model, i)) \
                 for i, model in enumerate(models)
                ]
        await asyncio.gather(*tasks)
        if "best_sentence" not in st.session_state:
            st.session_state["best_sentence"] = ""

with col1:
    if "input_text" not in st.session_state:
        st.session_state["input_text"] = ""
    text = st.text_area(
        "교정할 문장을 입력하세요:", height=400, key="input_text",
         value=st.session_state["input_text"]
    )

    finetuned_models = st.text_input(
        "기본 모델 외에 추가로 사용할 모델을 입력하세요(쉼표로 구분):", ""
    )
    finetuned_models = [
        model.strip() for model in finetuned_models.split(",") if model.strip()
        ]

    if st.button("교정"):
        asyncio.run(main())

with col2:
    for i in range(len([default_model]) + len(finetuned_models)):
        model_alias = f"기본 모델" if i == 0 else f"파인튜닝 모델 {i}"
        if model_alias in st.session_state:
            if st.button(model_alias, key=f"select_{model_alias}"):
                st.session_state["best_sentence"] = st.session_state[model_alias]
            st.text_area(
                model_alias, st.session_state[model_alias], height=180,
                key=f"display_{model_alias}"
            )

if "best_sentence" not in st.session_state:
    st.session_state["best_sentence"] = ""

best_sentence = st.text_area(
    "최적의 문장을 입력하거나 위에서 선택하세요:", 
    height=200, 
    key="best_sentence"
)

if st.button("TTS로 듣기"):
    response = client.audio.speech.create(
        model="tts-1", voice="alloy", input=best_sentence
    )
    audio_data = BytesIO(response.read())
    st.audio(audio_data, format='audio/mpeg')

if "sentences" not in st.session_state:
    st.session_state.sentences = []

if st.button("저장"):
    st.session_state.sentences.append({"original": text, "corrected": best_sentence})
    st.success("문장 쌍이 저장되었습니다.")

    df = pd.DataFrame(st.session_state.sentences)
    tsv = df.to_csv(sep="\t", index=False)
    b = BytesIO()
    b.write(tsv.encode())
    b.seek(0)
    st.download_button(
        label="TSV 다운로드",
        data=b,
        file_name="corrected_sentences.tsv",
        mime="text/tsv"
    )