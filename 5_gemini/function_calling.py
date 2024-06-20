import google.generativeai as genai

def get_price(product: str)-> int: 
    """제품의 가격을 알려주는 함수

    Args:
        theme: 제품명
    """    
    return 1000


def get_temperature(city: str)-> float: 
    """도시의 온도를 알려주는 함수

    Args:
        genre: 도시명
    """    
    return 20.5

model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", tools=[get_price, get_temperature])
chat_session = model.start_chat(enable_automatic_function_calling=True)
response = chat_session.send_message("서울의 온도는?")
print(response.text)
