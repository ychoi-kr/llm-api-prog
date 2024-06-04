from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Chroma

loader = CSVLoader(file_path="../../data/한국산업은행_금융 관련 용어_20151231.csv", encoding='cp949')
docs = loader.load()

print(docs[:2])

hf_model = HuggingFaceEmbeddings(model_name='jhgan/ko-sroberta-multitask')
Chroma.from_documents(docs, hf_model, persist_directory="./database")
