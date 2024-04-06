import streamlit as st
from openai import OpenAI
import numpy as np
import json
import plotly.graph_objects as go

st.title("상품 리뷰 분석 및 시각화")

# Streamlit 시크릿에서 OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 리뷰 입력 받기
reviews_input = st.text_area("상품 리뷰를 입력하세요 (리뷰 간 줄바꿈으로 구분):", height=200)

if st.button("리뷰 분석 및 시각화"):
    # 입력된 리뷰를 줄바꿈 기준으로 분리
    reviews = reviews_input.split("\n")
    
    # 리뷰 분석을 위한 프롬프트
    analysis_prompt = """
    다음은 상품에 대한 고객 리뷰입니다. 각 리뷰를 분석하여 다음 카테고리별로 1부터 5까지의 점수를 JSON 형식으로 출력해 주세요.
    카테고리: 품질, 배송, 가격, 고객서비스
    출력 형식: {"품질": 점수, "배송": 점수, "가격": 점수, "고객서비스": 점수}
    """
    
    # 리뷰 분석
    analyzed_reviews = []
    for review in reviews:
        # OpenAI API를 사용하여 리뷰 분석
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": analysis_prompt},
                {"role": "user", "content": review}
            ],
            max_tokens=100
        )
        analyzed_review = response.choices[0].message.content.strip()
        analyzed_reviews.append(analyzed_review)
    
    # 분석된 리뷰 출력
    st.subheader("분석된 리뷰")
    st.write("\n".join(analyzed_reviews))
    
    # JSON 파싱
    category_scores = {"품질": [], "배송": [], "가격": [], "고객서비스": []}
    for analyzed_review in analyzed_reviews:
        try:
            scores = json.loads(analyzed_review)
            for category, score in scores.items():
                category_scores[category].append(score)
        except json.JSONDecodeError:
            st.warning(f"다음 리뷰는 JSON 형식이 아닙니다: {analyzed_review}")
    
    # 카테고리별 평균 점수 계산
    category_avg_scores = {category: np.mean(scores) if scores else 0 for category, scores in category_scores.items()}
    
    # Plotly 극좌표계 차트 그리기
    fig = go.Figure()
    
    categories = list(category_avg_scores.keys())
    scores = list(category_avg_scores.values())
    categories.append(categories[0])  # 처음 카테고리를 리스트 끝에 추가하여 차트를 완성합니다.
    scores.append(scores[0])  # 처음 점수를 리스트 끝에 추가합니다.
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=False
    )
    
    # Streamlit에 Plotly 차트 표시
    st.plotly_chart(fig, use_container_width=True)
