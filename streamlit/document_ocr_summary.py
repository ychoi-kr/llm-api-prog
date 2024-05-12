import streamlit as st
import cv2
from PIL import Image
import numpy as np
import requests
from openai import OpenAI

# Streamlit 페이지 설정 
st.set_page_config(layout="wide")

# 타이틀
st.title("Upstage Document OCR and Summarization")

# API 키 설정
api_key = st.secrets["UPSTAGE_API_KEY"]

def summarize_text(text):
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.upstage.ai/v1/solar"
    )
    try:
        response = client.chat.completions.create(
            model="solar-1-mini-chat",
            messages=[
                {"role": "system", "content": "Summarize text with bullets."},
                {"role": "user", "content": text}
            ],
        )
        print("Summary generated.")
        summarized_text = response.choices[0].message.content
        return summarized_text
    except Exception as e:
        st.error(f"Summarization failed: {str(e)}")
        return None

# 이미지 업로드
uploaded_file = st.file_uploader("Upload image:", type=["png", "jpg", "jpeg"])

# OCR 실행 버튼
if st.button("Read it!"):
    st.session_state['ocr_clicked'] = True

def display_ocr_results(image, result):
    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption='Processed Image', use_column_width=True)

    with col2:
        st.write("Text in image:")
        if "pages" in result:
            full_text = result["pages"][0]["text"]
        else:
            full_text = ""

        # OCR 결과를 코드 블록으로 표시(복사하기 편리하도록)  
        if full_text:
            st.code(full_text)

if uploaded_file is not None and 'ocr_clicked' in st.session_state and \
        st.session_state['ocr_clicked']:
    # 이미지를 OpenCV 형식으로 변환
    image = Image.open(uploaded_file)
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # 업스테이지 API OCR 요청
    url = "https://api.upstage.ai/v1/document-ai/ocr"
    headers = {"Authorization": f"Bearer {api_key}"}

    # 이미지 파일을 바이트로 읽기
    image_bytes = uploaded_file.getvalue()

    # 업스테이지 OCR API에 전송할 파일 준비
    files = {"document": (uploaded_file.name, image_bytes, uploaded_file.type)}
    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        result = response.json()
        st.session_state['ocr_result'] = result
    else:
        st.error(f"OCR API request failed with status code {response.status_code}")
        print(response.text)  # 오류 메시지 출력
    st.session_state['original_image'] = img.copy()
    st.session_state['ocr_clicked'] = False

if 'ocr_result' in st.session_state:
    display_ocr_results(st.session_state['original_image'],
                        st.session_state['ocr_result'])

    # OCR로 추출한 텍스트
    extracted_text = st.session_state['ocr_result']["pages"][0]["text"] \
        if "pages" in st.session_state['ocr_result'] else ""

    if st.button("Summarize Text"):
        summary = summarize_text(extracted_text)
        st.write("Summary:")
        st.write(summary)
