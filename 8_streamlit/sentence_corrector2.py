import streamlit as st
from openai import AsyncOpenAI, OpenAI
import asyncio
import pandas as pd
from io import BytesIO

default_model = "gpt-4o-mini"

st.set_page_config(layout="wide")

st.title("Multi-Model Sentence Corrector")
st.text(f"OpenAI의 기본 모델({default_model})과 사용자의 파인튜닝 모델을 사용해 문장을 교정합니다.")

# OpenAI 및 Upstage 클라이언트 생성
openai_api_key = st.secrets["OPENAI_API_KEY"]
upstage_api_key = st.secrets["UPSTAGE_API_KEY"]
upstage_base_url = "https://api.upstage.ai/v1/solar"

# OpenAI 클라이언트 (TTS용)
client = OpenAI(api_key=openai_api_key)

# 클라이언트 딕셔너리 생성
clients = {
    'openai': AsyncOpenAI(api_key=openai_api_key),
    'upstage': AsyncOpenAI(api_key=upstage_api_key, base_url=upstage_base_url)
}

col1, col2 = st.columns([0.3, 0.7])

def generate_model_alias(i, model_name):
    if i == 0:
        return "기본 모델"
    else:
        # 특수 문자 대체 및 길이 제한
        safe_name = model_name.replace(':', '_').replace('\n', '').replace('\r', '')
        if len(safe_name) > 30:
            safe_name = safe_name[:27] + '...'
        return f"모델 {i}: {safe_name}"

async def correct(text, model_name, client_type):
    messages = [
        {"role": "system", "content": "다음 문장을 자연스러운 언어로 교정해 주세요."},
        {"role": "user", "content": text}
    ]

    client = clients[client_type]

    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.0
        )
        corrected_text = response.choices[0].message.content.strip()
    except Exception as e:
        corrected_text = f"에러 발생: {str(e)}"

    return corrected_text

async def main():
    if text.strip() == "":
        st.warning("문장을 입력해 주세요.")
    else:
        models = [default_model] + finetuned_models
        tasks = []
        st.session_state["model_aliases"] = []

        for i, model_name in enumerate(models):
            model_name = model_name.strip()
            if not model_name:
                continue

            # 모델명에 따라 클라이언트 선택
            if 'gpt' in model_name.lower():
                client_type = 'openai'
            elif 'solar' in model_name.lower():
                client_type = 'upstage'
            else:
                st.error(f"모델명을 분석할 수 없습니다: {model_name}")
                continue

            # 모델 별칭 생성
            model_alias = generate_model_alias(i, model_name)

            # 교정 작업 생성
            task = asyncio.create_task(
                correct(text, model_name, client_type)
            )
            tasks.append((task, model_alias, i))

            # 모델 별칭 저장
            st.session_state["model_aliases"].append((model_alias, i))

        # 교정 작업 실행 및 결과 저장
        for task, model_alias, i in tasks:
            corrected_text = await task
            st.session_state[model_alias] = corrected_text

        if "best_sentence" not in st.session_state:
            st.session_state["best_sentence"] = ""

with col1:
    if "input_text" not in st.session_state:
        st.session_state["input_text"] = ""
    text = st.text_area(
        "교정할 문장을 입력하세요:", height=400, key="input_text",
        value=st.session_state["input_text"]
    )

    finetuned_models_input = st.text_input(
        "기본 모델 외에 추가로 사용할 모델을 입력하세요(쉼표로 구분):", ""
    )
    finetuned_models = [
        model.strip() for model in finetuned_models_input.split(",") if model.strip()
    ]

    if st.button("교정"):
        asyncio.run(main())

with col2:
    if "model_aliases" in st.session_state:
        for model_alias, i in st.session_state["model_aliases"]:
            if model_alias in st.session_state:
                button_key = f"select_{i}"
                if st.button(f"{model_alias} 선택", key=button_key):
                    st.session_state["best_sentence"] = st.session_state[model_alias]
                text_area_key = f"display_{i}"
                st.text_area(
                    model_alias, st.session_state[model_alias], height=180,
                    key=text_area_key
                )

if "best_sentence" not in st.session_state:
    st.session_state["best_sentence"] = ""

best_sentence = st.text_area(
    "최적의 문장을 입력하거나 위에서 선택하세요:",
    height=200,
    key="best_sentence"
)

if st.button("TTS로 듣기"):
    try:
        response = client.audio.speech.create(
            model="tts-1", voice="alloy", input=best_sentence
        )
        audio_data = BytesIO(response.read())
        st.audio(audio_data, format='audio/mpeg')
    except Exception as e:
        st.error(f"TTS 생성 중 에러 발생: {str(e)}")

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
