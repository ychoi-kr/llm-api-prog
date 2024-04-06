import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="BMI 계산기", page_icon=":scales:", layout="wide")

st.title("BMI 계산기")
st.write("체질량지수(BMI)를 계산해 보세요!")

height = st.number_input("키를 입력하세요 (cm):", min_value=100, max_value=250, value=160)
weight = st.number_input("몸무게를 입력하세요 (kg):", min_value=30, max_value=200, value=60)

if st.button("BMI 계산"):
    bmi = weight / ((height/100) ** 2)
    st.subheader(f"당신의 BMI는 {bmi:.1f}입니다.")

    bmi_category = ""
    if bmi < 18.5:
        bmi_category = "저체중"
    elif bmi < 23:
        bmi_category = "정상"
    elif bmi < 25:
        bmi_category = "과체중"
    else:
        bmi_category = "비만"

    bmi_data = {
        "지표": ["BMI", "범주"],
        "값": [f"{bmi:.1f}", bmi_category]  # BMI 값을 문자열로 변환
    }

    st.table(bmi_data)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bmi,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "BMI"},
        gauge={
            'axis': {'range': [None, 40]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 18.5], 'color': "lightblue"},
                {'range': [18.5, 25], 'color': "green"},
                {'range': [25, 30], 'color': "orange"},
                {'range': [30, 40], 'color': "red"}
            ],
        }
    ))

    st.plotly_chart(fig)
