from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


prompt_template = "{topic}에 관해 짧은 농담을 해봐"
prompt = PromptTemplate(input_variables=["topic"], template=prompt_template)
output_parser = StrOutputParser()
model = ChatOpenAI(model="gpt-3.5-turbo")
chain = LLMChain(prompt=prompt, llm=model, output_parser=output_parser)
result = chain.invoke({"topic": "아이스크림"})
print(result["text"])
