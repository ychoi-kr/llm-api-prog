import google.generativeai as genai  
system_instruction="json 형식으로 답할 것. 키에는 키워드를 넣고, 값에는 내용을 넣을 것. 3개를 넘기지 말 것"
model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=system_instruction)
chat_session = model.start_chat(history=[]) #ChatSession 객체 반환 
user_queries = ["인공지능의 특징이 뭐에요?", "어떤 것들을 조심해야 하죠?"] 

for user_query in user_queries: 
    print(f'[사용자]: {user_query}')    
    response = chat_session.send_message(user_query) 
    print(f'[모델]: {response.text}') 