import google.generativeai as genai  
system_instruction="당신은 유치원 선생님입니다. 사용자는 유치원생입니다. 쉽고 친절하게 이야기하되 3문장 이내로 짧게 얘기하세요."
model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=system_instruction)
chat_session = model.start_chat(history=[]) #ChatSession 객체 반환 
user_queries = ["인공지능이 뭐에요?", "그럼 스스로 생각도 해요?"] 
for user_query in user_queries: 
    print(f'[사용자]: {user_query}')    
    response = chat_session.send_message(user_query) 
    print(f'[모델]: {response.text}') 