import google.generativeai as genai 
import PIL.Image # 설치: pip install pillow 

image_data = PIL.Image.open("../data/monalisa.jpg") # 모나리자 그림 
model = genai.GenerativeModel('gemini-1.5-flash-latest') 
response = model.generate_content(["이 그림에 대해 한 문장으로 설명하세요.", image_data]) 
print(response.text) 
print(f"건수: {len(response.candidates)}") 
print("="*50) 

for candidate in response.candidates: 
    print(candidate) 