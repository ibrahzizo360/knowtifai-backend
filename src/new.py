from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains import create_retrieval_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains.history_aware_retriever import create_history_aware_retriever



def load_docs():
    # Load PDF Documents
    pdf_path = "./pdf/8.pdf"
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    return pages

def create_vector_store(pages):
    # Create Vector Store and Retrieval System
    embedding = OpenAIEmbeddings()
    db = FAISS.from_documents(pages, embedding=embedding)

    return db


def create_chain(vectorStore):
    model = ChatOpenAI(
        temperature=0.4,
        model='gpt-3.5-turbo-1106'
    )

    prompt = ChatPromptTemplate.from_template("""
    Answer the user's question.If you don't know the answer, just say that you don't know, 
    don't try to make up an answer.
    Context: {context}
    Question: {input}
    """)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's questions based on the context: {context}. If you don't know the answer, just say that you don't know, don't try to make up an answer."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

    # chain = prompt | model
    document_chain = create_stuff_documents_chain(
        llm=model,
        prompt=prompt
    )

    retriever = vectorStore.as_retriever(search_kwargs={"k": 3})
    
    retriever_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    history_aware_retriever = create_history_aware_retriever(
        llm=model,
        retriever=retriever,
        prompt=retriever_prompt
    )

    retrieval_chain = create_retrieval_chain(history_aware_retriever, document_chain)

    return retrieval_chain


docs = load_docs()
vectorStore = create_vector_store(docs)
chain = create_chain(vectorStore)

chat_history = [
    HumanMessage(content="Hello", sender="user"),
    AIMessage(content="Hi there!", sender="system"),
    HumanMessage(content="My name is Zizo"),
]

response = chain.invoke({
    "input": "What is the formula for random Forest?",
    "chat_history": chat_history,
})

print(response)