import streamlit as st
from openai import OpenAI
from pydantic import BaseModel
import numpy as np
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
    다음은 상품에 대한 고객 리뷰입니다. 각 리뷰를 분석하여 다음 카테고리별로 1부터 5까지의 점수를 부여하세요.
    카테고리: 품질, 배송, 가격, 고객서비스
    """

    # Pydantic 모델 정의
    class ReviewAnalysis(BaseModel):
        품질: int
        배송: int
        가격: int
        고객서비스: int
    
    # 카테고리별 점수 수집 초기화
    category_scores = {"품질": [], "배송": [], "가격": [], "고객서비스": []}

    # 리뷰 분석
    analyzed_reviews = []
    for review in reviews:
        # OpenAI API를 사용하여 리뷰 분석
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": analysis_prompt},
                    {"role": "user", "content": review}
                ],
                response_format=ReviewAnalysis
            )
            message = completion.choices[0].message
            if message.parsed:
                parsed_result = message.parsed
                analyzed_reviews.append(parsed_result)
                # 카테고리별 점수 수집
                for category in category_scores.keys():
                    category_scores[category].append(getattr(parsed_result, category))
            elif message.refusal:
                st.warning(f"리뷰 분석을 거부했습니다: {review}")
            else:
                st.warning(f"리뷰 분석에 실패했습니다: {review}")
        except Exception as e:
            st.warning(f"리뷰 분석 중 오류가 발생했습니다: {review}\n오류 메시지: {e}")
    
    # 분석된 리뷰 출력
    st.subheader("분석된 리뷰 점수")
    for idx, analyzed_review in enumerate(analyzed_reviews):
        st.write(f"리뷰 {idx+1}: {analyzed_review.dict()}")

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
