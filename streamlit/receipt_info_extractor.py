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
            
            expense_details = []
            date = None
            total_amount = None
            payment_method = None
            card_number = None
            
            for field in receipt_data['fields']:
                print(field)
                if field['key'].startswith('group'):
                    product_name = None
                    product_price = None
                    for prop in field['properties']:
                        if prop['key'].endswith('product_name'):
                            product_name = prop['value']
                        elif prop['key'].endswith('unit_product_total_price_before_discount'):
                            product_price = prop['value']
                    if product_name and product_price:
                        expense_details.append(f"{product_name}: {product_price}")
                elif field['key'] == 'date.date':
                    date = field['value']
                elif field['key'] == 'transaction.transaction_date' and field['type'] == 'content':
                    date = field['value']
                elif field['key'] == 'total.charged_price' and field['type'] == 'content':
                    total_amount = field['value']
                elif field['key'] == 'transaction.cc_code' and field['type'] == 'content':
                    payment_method = field['value']
                elif field['key'] == 'total.card_payment_price' and field['type'] == 'header':
                    if '쿠페이' in field['value']:
                        payment_method = '쿠페이'
                elif field['key'] == 'payment.credit_card_number':
                    card_number = field['value']
            
            st.write("지출 상세 내역:")
            for detail in expense_details:
                st.write(f"- {detail}")
            
            if date:
                st.write(f"거래일시: {date}")
            else:
                st.write("거래일시를 찾을 수 없습니다.")
            
            if total_amount:
                st.write(f"합계 금액: {total_amount}")
            else:
                st.write("합계 금액을 찾을 수 없습니다.")

            if payment_method:
                st.write(f"지불 수단: {payment_method}")
            else:
                st.write("지불 수단을 찾을 수 없습니다.")
            
            if card_number:
                st.write(f"카드 번호: {card_number}")
            else:
                st.write("카드 번호를 찾을 수 없습니다.")
        else:
            st.error("영수증 정보를 추출할 수 없습니다. 다른 영수증 이미지를 시도해 주세요.")