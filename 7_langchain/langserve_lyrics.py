from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langserve import add_routes

# Initialize the FastAPI app
app = FastAPI()

# Set up the OpenAI model with the appropriate API key configuration
openai_model = ChatOpenAI(
    model="gpt-4-turbo",
    temperature=1.2
)

# Create a prompt template
prompt = ChatPromptTemplate.from_template("{topic}에 관해 노랫말을 써줘.")

# Combine the model and prompt into a chain
chain = prompt | openai_model

# Add routes to the app that serve the chain
add_routes(app, chain, path="/lyrics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
