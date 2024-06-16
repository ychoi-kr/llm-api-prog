import streamlit as st
from PIL import Image
import requests
import base64
from io import BytesIO

def encode_image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

st.title("이미지 설명 생성기")

uploaded_image = st.file_uploader("이미지를 업로드하세요:", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    
    # EXIF 데이터에서 회전 정보 확인 및 조정
    exif = image._getexif()
    if exif:
        orientation = exif.get(0x0112)
        if orientation == 3:
            image = image.rotate(180, expand=True)
        elif orientation == 6:
            image = image.rotate(270, expand=True)
        elif orientation == 8:
            image = image.rotate(90, expand=True)
    
    st.image(image, caption='업로드된 이미지', use_column_width=True)

    if st.button("이미지 설명 생성"):
        base64_image = encode_image_to_base64(image)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "이미지에 무엇이 있나요?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload).json()
        
        if 'choices' in response and len(response['choices']) > 0:
            description = response['choices'][0]['message']['content']
            st.success("이미지 설명 생성 완료!")
            st.write(description)
        else:
            st.error("이미지를 분석할 수 없습니다.")
