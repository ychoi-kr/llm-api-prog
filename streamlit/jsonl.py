import streamlit as st
import pandas as pd
import json
import os

def load_data(file):
    file_type = file.name.split('.')[-1]
    separator = ',' if file_type == 'csv' else '\t' if file_type == 'tsv' else None
    return pd.read_csv(file, sep=separator, encoding='utf-8', quotechar='"')

def convert_to_jsonl(df, format_choice, system_prompt=""):
    if format_choice == "conversational single-turn chat":
        return "\n".join(df.apply(lambda x: json.dumps({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": x.iloc[0]},
                {"role": "assistant", "content": x.iloc[1]}
            ]
        }, ensure_ascii=False), axis=1))
    elif format_choice == "prompt completion pair":
        return "\n".join(df.apply(lambda x: json.dumps({
            "prompt": x.iloc[0],
            "completion": x.iloc[1]
        }, ensure_ascii=False), axis=1))
    return ""

st.title('CSV/TSV to JSONL Converter for OpenAI Fine-Tuning')

uploaded_file = st.file_uploader("Choose a CSV or TSV file", type=['csv', 'tsv'])

if uploaded_file is not None:
    if 'df' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
        st.session_state.df = load_data(uploaded_file)
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.jsonl_str = ""  # Reset JSONL string on new file upload
    st.write(st.session_state.df)

    format_choice = st.selectbox("Select the format for fine-tuning:",
                                 ["Select format",
                                  "conversational single-turn chat",
                                  "prompt completion pair"
                                  ])

    if format_choice == "conversational single-turn chat":
        default_prompt = "Marv is a factual chatbot that is also sarcastic."
        system_prompt = st.text_input("System Prompt", default_prompt)

    if st.button("Convert to JSONL"):
        st.session_state.jsonl_str = convert_to_jsonl(
            st.session_state.df,
            format_choice,
            system_prompt if format_choice == "conversational single-turn chat" else ""
            )

if st.session_state.get('jsonl_str'):
    # 결과 출력
    st.text_area("JSONL Output", st.session_state.jsonl_str, height=300)

    # 파일로 다운로드
    download_filename = f"{os.path.splitext(st.session_state.uploaded_file_name)[0]}.jsonl"
    st.download_button(label="Download JSONL",
                       data=st.session_state.jsonl_str.encode('utf-8'),
                       file_name=download_filename,
                       mime='text/plain')
