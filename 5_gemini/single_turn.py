import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# genai.configure(api_key=userdata.get('GOOGLE_API_KEY')) 구글 코랩인 경우 
#model = genai.GenerativeModel('gemini-pro')
model = genai.GenerativeModel('gemini-1.5-flash-latest')
response = model.generate_content("인공지능에 대해 한 문장으로 설명하세요.")
print(response.text)
