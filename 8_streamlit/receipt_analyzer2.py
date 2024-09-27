import streamlit as st
from PIL import Image
import requests
from io import BytesIO


api_key = st.secrets['UPSTAGE_API_KEY']

def extract_receipt_info(image): 
    url = "https://api.upstage.ai/v1/document-ai/extraction"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    files = {"document": buffered.getvalue()}
    data = {"model": "receipt-extraction"}
    response = requests.post(url, headers=headers, files=files, data=data)
    return response.json()


st.title("영수증 정보 추출기")
uploaded_image = st.file_uploader("영수증 이미지를 업로드하세요:", type=["jpg", "jpeg", "png"])

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
    
    st.image(image, caption='업로드된 영수증 이미지', use_column_width=True)

    if st.button("영수증 정보 추출"):
        receipt_data = extract_receipt_info(image)
        
        if 'fields' in receipt_data:
            st.success("영수증 정보 추출 완료!")
            
            # 추출된 필드들을 출력
            for field in receipt_data.get('fields', []):
                key = field.get('key', '')
                value = field.get('refinedValue', field.get('value', ''))
                st.write(f"{key}: {value}")
        else:
            st.error("영수증 정보를 추출할 수 없습니다. 다른 영수증 이미지를 시도해 주세요.")
