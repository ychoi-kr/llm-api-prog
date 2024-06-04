import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash-latest')
response = model.generate_content("인공지능에 대해 자세히 설명해줘.", stream=True)

for no, chunk in enumerate(response, start=1):
  print(f"{no}: {chunk.text}")
  print("="*50)

ss