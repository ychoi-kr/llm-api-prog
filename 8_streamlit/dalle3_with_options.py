import streamlit as st
from openai import OpenAI

# OpenAI API 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 스트림릿 UI 구성
st.title("DALL-E 3 Image Creation with Options")

image_type = st.selectbox(
    "Image type:",
    [
        "general image",
        "icon",
        "logo",
        "tatoo design",
        "die-cut sticker",
        "minecraft skin",
        "custom emoji",
        "personalized bitmoji-style avatar",
        "personalized greeting card",
        "a poster",
        "a flyer",
    ]
)

user_prompt = st.text_input("What do you want to see?", "a cute cat")
style_option = st.selectbox("Image style:", ["natural", "vivid"], index=1)
quality_option = st.radio("Quality:", ["standard", "hd"], index=1)
aspect_ratio = st.selectbox("Aspect ratio:", ["1024x1024", "1792x1024", "1024x1792"])

def modify_prompt_based_on_selection(prompt, image_type):
    modified_prompt = image_type + " of " + prompt
    return modified_prompt

# 이미지 생성 및 표시
if st.button("Create Image"):
    # 사용자 선택에 따른 프롬프트 수정
    modified_prompt = modify_prompt_based_on_selection(user_prompt, image_type)

    # DALL-E 3 API 호출
    response = client.images.generate(
        model="dall-e-3",
        prompt=modified_prompt,
        style=style_option,
        quality=quality_option,
        size=aspect_ratio,
        n=1,
        response_format="url"
    )

    # API 응답 처리
    if response.data:
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt
        
        # 생성된 이미지 표시
        st.image(image_url, caption="Created Image", use_column_width=True)
        
        # 수정된 프롬프트 표시
        st.write(f"Revised prompt: {revised_prompt}")
    else:
        st.write("Failed to generate image. Please try again.")
