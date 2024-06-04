from vertexai.preview.generative_models import GenerativeModel 
import vertexai 
import os 
# 키 위치를 환경변수 GOOGLE_APPLICATION_CREDENTIALS에 담아두면 아래 코드는 필요 없음 
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = \
"D:/google_key/_gemini/robotic-vista-415814-20055e13b7a2.json"

vertexai.init(project="robotic-vista-415814", location="asia-northeast3") 

user_message = "인공지능에 대해 한 문장으로 말하세요." 
model = GenerativeModel(model_name='gemini-1.5-flash-preview-0514')
resp = model.generate_content(user_message) 
print(resp.text) 


