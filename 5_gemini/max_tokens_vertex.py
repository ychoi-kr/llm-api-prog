# vertex ai 사용 방법은 이 챕터 뒤에서 다룹니다.
import vertexai.generative_models as models 
import vertexai
vertexai.init(project="your-project-id", location="asia-northeast3") 
generation_config = models.GenerationConfig(max_output_tokens=10) 
model = models.GenerativeModel('gemini-1.5-flash-preview-0514', generation_config=generation_config) 
user_message = "인공지능에 대해 한 문장으로 설명하세요." 
response = model.generate_content(user_message) 
print(f'토큰 수: {model.count_tokens(response.text).total_tokens}') 
print(response._raw_response) 