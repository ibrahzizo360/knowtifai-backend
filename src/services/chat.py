from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains import create_retrieval_chain,RetrievalQAWithSourcesChain,ConversationalRetrievalChain
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains.history_aware_retriever import create_history_aware_retriever
import uuid
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks import AsyncIteratorCallbackHandler
from services.callbacks import MyCustomHandler   
from langchain_community.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from db import MONGODB_COLLECTION, ATLAS_VECTOR_SEARCH_INDEX_NAME
from queue import Queue

upload_streamer_queue = Queue()
chat_streamer_queue = Queue()

def generate_session_id():
    """
    Generate a random session ID using UUID (Universally Unique Identifier).
    """
    return str(uuid.uuid4())

def load_docs(file_path):
    # Load PDF Documents
    pdf_path = file_path
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    return pages

def create_vector_store(pages):
    # Create Vector Store and Retrieval System
    
    db = MongoDBAtlasVectorSearch.from_documents(
    documents=pages,
    embedding=OpenAIEmbeddings(disallowed_special=()),
    collection=MONGODB_COLLECTION,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
)
    return db


def create_upload_chain(vectorStore):
    model = ChatOpenAI(
        temperature=0.4,
        model='gpt-3.5-turbo-1106'
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Answer the user's questions based on the context: {context}.
         If you don't know the answer, just say that you don't know, don't try to make up an answer.
         """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

    document_chain = create_stuff_documents_chain(
        llm=model,
        prompt=prompt
    )

    retriever = vectorStore.as_retriever(search_kwargs={"k": 1})
    
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
    
    llm = ChatOpenAI(temperature=0.3, 
                max_retries=3,
                 callbacks=[AsyncIteratorCallbackHandler()],
                 streaming=True)
    
    my_handler = MyCustomHandler(upload_streamer_queue)
    
    streaming_llm = ChatOpenAI(
            max_retries=15,
            temperature=0.3,
            callbacks=[my_handler],
            streaming=True,
        )
    
    
    chain = ConversationalRetrievalChain.from_llm(llm=streaming_llm, 
                                                  retriever=retriever,
                                                  return_source_documents=True,)

    return chain

def create_chat_chain(vectorStore):
    model = ChatOpenAI(
        temperature=0.4,
        model='gpt-3.5-turbo-1106'
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Answer the user's questions based on the context: {context}.
         If you don't know the answer, just say that you don't know, don't try to make up an answer.
         """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

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
    
    my_handler = MyCustomHandler(chat_streamer_queue)
    
    streaming_llm = ChatOpenAI(
            max_retries=15,
            temperature=0.3,
            callbacks=[my_handler],
            streaming=True,
        )

    chain = ConversationalRetrievalChain.from_llm(llm=streaming_llm, 
                                                  retriever=retriever,
                                                  return_source_documents=True,)

    return chain

def create_default_chain(vectorStore):
    model = ChatOpenAI(
        temperature=0.4,
        model='gpt-3.5-turbo-1106'
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Answer the user's questions based on the context: {context}.
         If you don't know the answer, just say that you don't know, don't try to make up an answer.
         """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

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
    
    llm = ChatOpenAI(temperature=0.3, 
                max_retries=3,
                 callbacks=[AsyncIteratorCallbackHandler()],
                 streaming=True)
    
    
    chain = ConversationalRetrievalChain.from_llm(llm=llm, 
                                                  retriever=retriever,
                                                  return_source_documents=True,)

    return chain


streaming_callback_handler = MyCustomHandler(upload_streamer_queue)

