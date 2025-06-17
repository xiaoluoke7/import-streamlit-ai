from langchain_chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
import os
import requests
from langchain.embeddings.base import Embeddings

# 先定义 OllamaEmbeddings 类
class OllamaEmbeddings(Embeddings):
    def __init__(self, model="bge-m3:latest", api_url="http://localhost:11434/api/embeddings"):
        self.model = model
        self.api_url = api_url

    def embed_documents(self, texts):
        return [self._embed(text) for text in texts]

    def embed_query(self, text):
        return self._embed(text)

    def _embed(self, text):
        data = {
            "model": self.model,
            "prompt": text
        }
        response = requests.post(self.api_url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()["embedding"]

# 初始化 embedding 模型
embeddings = OllamaEmbeddings(model="bge-m3:latest")

# 知识库存储路径
VECTOR_DB_PATH = "chroma_knowledge_base"

def build_knowledge_base(texts, metadatas=None):
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.create_documents(texts, metadatas=metadatas)
    db = Chroma.from_documents(docs, embeddings, persist_directory=VECTOR_DB_PATH)

def load_knowledge_base():
    if not os.path.exists(VECTOR_DB_PATH):
        return None
    return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)

def add_to_knowledge_base(texts, metadatas=None):
    db = load_knowledge_base()
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    if metadatas is not None:
        # 自动扩展 metadatas 长度
        docs = text_splitter.create_documents(texts, metadatas=metadatas * len(texts) if len(metadatas) == 1 else metadatas)
    else:
        docs = text_splitter.create_documents(texts)
    if db is None:
        build_knowledge_base(texts, metadatas)
    else:
        db.add_documents(docs)

def search_knowledge_base(query, top_k=3):
    db = load_knowledge_base()
    if db is None:
        return []
    docs_and_scores = db.similarity_search_with_score(query, k=top_k)
    return [doc.page_content for doc, score in docs_and_scores]

def delete_by_filename(filename):
    db = load_knowledge_base()
    if db is None:
        return
    db.delete(where={"filename": filename}) 