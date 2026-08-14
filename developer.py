'''
In this File we are going to load the data from each department
and by following the RAG pipeline we are going to save the data in
vector DB individually
'''
import os
import numpy as np
import langchain
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai.chat_models import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai_embeding = OpenAIEmbeddings(model = "text-embedding-3-small")
openai_llm = ChatOpenAI(model = "gpt-4o")

for i in os.listdir("./data"):
    d = TextLoader("./data/"+i)
    print(f"Data Collected Successfully from : {i} : file")

    chunk_obj = RecursiveCharacterTextSplitter(chunk_size=300 , chunk_overlap=100)
    result = chunk_obj.split_documents(d.load())
    print(f"Number of Chunks in : {i} : File was : {len(result)}")

    chroma_db = Chroma.from_documents(result , openai_embeding , persist_directory="./db/"+i+" database")
    print(f"DB created Successfully for : {i}")

print(f"ALL DB created Successfully")
