import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from openai import OpenAI


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

def classify_expense(expense_details):
    client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1/solar")
    
    expense_text = ", ".join(expense_details)

    response = client.chat.completions.create(
        model="solar-mini",
        messages=[
            {"role": "system", "content": "지출 내역이나 매장 이름을 읽고, 생활비, 주거비, 교육양육비, 교통비, 통신비, 문화여가비, 기타 지출 중 하나로 분류하세요. 식재료는 '생활비 - 식비'로, 식당에서 사 먹거나 배달시킬 경우에는 '생활비 - 외식비'로, 안경이나 렌즈 구매는 '생활비 - 의료비'로 분류하세요. 전체 지출 내역을 단 한 가지로 분류해야 하며, 상세 내역이나 설명을 출력하지 마세요."},
            {"role": "user", "content": expense_text}
        ],
        stop='.',
    )
    
    return response.choices[0].message.content.strip('.')


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
            store_name = None
            date = None
            total_amount = None
            payment_price = None
            payment_method = None
            card_number = None
            
            for field in receipt_data.get('fields', []):
                key = field.get('key', '')
                field_type = field.get('type', '')
                value = field.get('refinedValue', field.get('value', ''))
                print(f"{key}: {value}")
                
                if key.startswith('group'):
                    product_name = None
                    product_price = None
                    for prop in field.get('properties', []):
                        prop_key = prop.get('key', '')
                        prop_value = prop.get('refinedValue', prop.get('value', ''))
                        if prop_key.endswith('product_name'):
                            product_name = prop_value
                        elif prop_key.endswith('unit_product_total_price_before_discount'):
                            product_price = prop_value
                    if product_name and product_price:
                        expense_details.append(f"{product_name}: {product_price}")

                # 상호명
                elif key == 'store.store_name' and field_type == 'content':
                    store_name = value

                # 거래일시
                elif key == 'transaction.transaction_date' and field_type == 'content':
                    if not date:
                        date = value
                elif key == 'date.date' and field_type == 'content':
                    if not date:
                        date = value

                # 합계
                elif key == 'total.charged_price' and field_type == 'content':
                    total_amount = value
                elif not total_amount and key in ['total.tax_price', 'total.subtotal_price'] and field_type == 'content':
                    if value.replace(',', '').isdigit():
                        total_amount = value
                
                # 결제액
                elif key in ['total.payment_price', 'total.card_payment_price'] and field_type == 'content':
                    payment_price = value
                
                # 지불 수단
                elif key == 'transaction.cc_code' and field_type == 'content':
                    payment_method = value
                elif key == 'total.card_payment_price' and field_type == 'header':
                    if '쿠페이' in value:
                        payment_method = '쿠페이'
                
                # 카드 번호
                elif key == 'payment.credit_card_number':
                    card_number = value
                elif key == 'transaction.cc_number' and field_type == 'content':
                    card_number = value
            
            # 지출 분류를 위한 입력 데이터 설정
            if expense_details:
                classification_input = expense_details
            elif store_name:
                classification_input = [store_name]
            else:
                classification_input = []
            
            expense_category = classify_expense(classification_input)
            
            output = ""            
            output += f"상호명: {store_name if store_name else '찾을 수 없음'}"
            output += f"\n거래일시: {date if date else '찾을 수 없음'}"
            
            if expense_details:
                output += "\n\n지출 상세 내역:\n"
                for detail in expense_details:
                    output += f"- {detail}\n"

            output += f"\n합계 금액: {total_amount if total_amount else '찾을 수 없음'}"
            output += f"\n결제액: {payment_price if payment_price else '찾을 수 없음'}"
            output += f"\n지불 수단: {payment_method if payment_method else '찾을 수 없음'}"
            output += f"\n카드 번호: {card_number if card_number else '찾을 수 없음'}"
            output += f"\n지출 분류: {expense_category}"
            
            st.code(output, language='plain')
        else:
            st.error("영수증 정보를 추출할 수 없습니다. 다른 영수증 이미지를 시도해 주세요.")
