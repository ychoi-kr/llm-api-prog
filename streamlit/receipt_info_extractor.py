import streamlit as st
from PIL import Image
import requests
from io import BytesIO

def extract_receipt_info(image):
    api_key = st.secrets['UPSTAGE_API_KEY']
    url = "https://api.upstage.ai/v1/document-ai/extraction/receipt"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    files = {"document": buffered.getvalue()}
    
    response = requests.post(url, headers=headers, files=files)
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
            
            for field in receipt_data['fields']:
                if field['key'] == 'store.store_name':
                    st.write(f"상호명: {field['value']}")
                elif field['key'] == 'total.subtotal_price':
                    st.write(f"소계: {field['value']}")
                elif field['key'] == 'total.tip_price':
                    st.write(f"팁: {field['value']}")  
                elif field['key'] == 'total.tax_price':
                    st.write(f"세금: {field['value']}")
                elif field['key'] == 'total.charged_price':
                    st.write(f"총계: {field['value']}")
        else:
            st.error("영수증 정보를 추출할 수 없습니다. 다른 영수증 이미지를 시도해주세요.")