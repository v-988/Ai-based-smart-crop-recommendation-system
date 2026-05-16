'''import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
#from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.chains import RetrievalQA
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.document_loaders import TextLoader


load_dotenv()

# load docs
docs = []
for file in os.listdir("docs"):
    if file.endswith(".txt"):
        loader = TextLoader("docs/" + file)
        docs.extend(loader.load())

# split
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
chunks = splitter.split_documents(docs)

# embeddings
embeddings = OpenAIEmbeddings()

# vector DB
vectorstore = FAISS.from_documents(chunks, embeddings)

# model
llm = ChatOpenAI(model="gpt-4o-mini")

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)

def ask_rag(q):
    return qa_chain.run(q)'''

'''2import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()

# -------------------------
# Load documents
# -------------------------
files = [
    "knowledge/soil.txt",
    "knowledge/crops.txt",
    "knowledge/schemes.txt",
    "knowledge/fertilizer.txt"
]

docs = []
for f in files:
    loader = TextLoader(f, encoding="utf-8")
    docs.extend(loader.load())

# -------------------------
# Split text
# -------------------------
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

splits = splitter.split_documents(docs)

# -------------------------
# Create embeddings
# -------------------------
embeddings = OpenAIEmbeddings()

vectorstore = FAISS.from_documents(splits, embeddings)

retriever = vectorstore.as_retriever()

# -------------------------
# LLM
# -------------------------
llm = ChatOpenAI(model="gpt-4o-mini")

# -------------------------
# Ask function (RAG logic)
# -------------------------
def ask_rag(question: str):

    relevant_docs = retriever.get_relevant_documents(question)

    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    prompt = f"""
You are an agriculture expert assistant.

Use this knowledge:
{context}

Answer clearly for farmers:
Question: {question}
"""

    response = llm.invoke(prompt)

    return response.content

if __name__ == "__main__":
    print(ask_rag("Which crop grows in red soil?"))'''

'''import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

load_dotenv()'''

'''@@@import os
from dotenv import load_dotenv

# loaders
from langchain_community.document_loaders import PyPDFLoader, TextLoader

# splitter (NEW package path)
from langchain_text_splitters import RecursiveCharacterTextSplitter

# vector store
from langchain_community.vectorstores import FAISS

# embeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

# LLM
from langchain_openai import ChatOpenAI

# chains (IMPORTANT — from langchain, not community)
from langchain.chains import RetrievalQA

load_dotenv()



DATA_PATH = "data"
INDEX_PATH = "faiss_index"

# -----------------------------
# Load Documents
# -----------------------------
def load_documents():
    docs = []
    if not os.path.exists(DATA_PATH):
        return docs

    for f in os.listdir(DATA_PATH):
        path = os.path.join(DATA_PATH, f)
        if f.endswith(".pdf"):
            docs.extend(PyPDFLoader(path).load())
        elif f.endswith(".txt"):
            docs.extend(TextLoader(path, encoding="utf-8").load())
    return docs


# -----------------------------
# Build or Load Vector DB (runs once)
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

if os.path.exists(INDEX_PATH):
    vectordb = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
else:
    documents = load_documents()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    chunks = splitter.split_documents(documents)
    vectordb = FAISS.from_documents(chunks, embeddings)
    vectordb.save_local(INDEX_PATH)

retriever = vectordb.as_retriever(search_kwargs={"k": 4})


# -----------------------------
# OpenRouter LLM
# -----------------------------
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="meta-llama/llama-3-8b-instruct",
    temperature=0.2,
    timeout=40
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff"
)


# -----------------------------
# Public function used by API
# -----------------------------
def ask_bot(question: str) -> str:
    try:
        return qa_chain.run(question)
    except Exception as e:
        return f"Error: {str(e)}"'''

import os
from dotenv import load_dotenv

# loaders
from langchain_community.document_loaders import PyPDFLoader, TextLoader

# splitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

# vector store
from langchain_community.vectorstores import FAISS

# embeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

# LLM
from langchain_openai import ChatOpenAI

# Modern replacement for RetrievalQA
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

DATA_PATH = "data"
INDEX_PATH = "faiss_index"

# -----------------------------
# Load Documents
# -----------------------------
def load_documents():
    docs = []
    if not os.path.exists(DATA_PATH):
        return docs

    for f in os.listdir(DATA_PATH):
        path = os.path.join(DATA_PATH, f)
        if f.endswith(".pdf"):
            docs.extend(PyPDFLoader(path).load())
        elif f.endswith(".txt"):
            docs.extend(TextLoader(path, encoding="utf-8").load())
    return docs


# -----------------------------
# Build or Load Vector DB (runs once)
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

if os.path.exists(INDEX_PATH):
    vectordb = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
else:
    documents = load_documents()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    chunks = splitter.split_documents(documents)
    vectordb = FAISS.from_documents(chunks, embeddings)
    vectordb.save_local(INDEX_PATH)

retriever = vectordb.as_retriever(search_kwargs={"k": 4})


# -----------------------------
# OpenRouter LLM
# -----------------------------
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="meta-llama/llama-3-8b-instruct",
    temperature=0.2,
    timeout=40
)

# -----------------------------
# Modern Chain (replaces RetrievalQA)
# -----------------------------
prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant. Answer the question based only on the provided context.
If the answer is not in the context, say "I don't know based on the provided documents."

Context: {context}

Question: {input}
""")

combine_chain = create_stuff_documents_chain(llm, prompt)
qa_chain = create_retrieval_chain(retriever, combine_chain)


# -----------------------------
# Public function used by API
# -----------------------------
def ask_bot(question: str) -> str:
    try:
        response = qa_chain.invoke({"input": question})
        return response["answer"]
    except Exception as e:
        return f"Error: {str(e)}"
