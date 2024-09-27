import streamlit as st
from PIL import Image

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
