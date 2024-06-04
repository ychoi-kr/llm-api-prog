import google.generativeai as genai 

model = genai.GenerativeModel('gemini-1.5-flash-latest') 
user_queries = [{'role':'user', 'parts': ["인공지능에 대해 한 문장으로 짧게 설명하세요."]}, 
                {'role':'user', 'parts': ["의식이 있는지 한 문장으로 답하세요."]} 
            ] 

history = [] 
for user_query in user_queries: 
    history.append(user_query) 
    print(f'[사용자]: {user_query["parts"][0]}')   
    response = model.generate_content(history) 
    print(f'[모델]: {response.text}')    
    history.append(response.candidates[0].content) 