from langchain_openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import StuffDocumentsChain, LLMChain, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from dotenv import load_dotenv
import os
load_dotenv()


# Load PDF Documents
pdf_path = "./pdf/3.pdf"
loader = PyPDFLoader(pdf_path)
pages = loader.load_and_split()

# Create Vector Store and Retrieval System
embeddings = OpenAIEmbeddings()
# db = FAISS.from_documents(pages, OpenAIEmbeddings())
# db = db.as_retriever(search_kwargs={"k": 3})
db = MongoDBAtlasVectorSearch.from_connection_string(
    os.getenv('MONGO_URL'),
    'embeddings.embeddings',
    OpenAIEmbeddings(disallowed_special=()),
    index_name='vector_index',
    )

# Define Prompt Templates and Chains
document_prompt = PromptTemplate(input_variables=["page_content"], template="{page_content}")

document_variable_name = "context"
model = ChatOpenAI(
        temperature=0.4,
        model='gpt-3.5-turbo-1106'
    )

# prompt = PromptTemplate.from_template("Summarize this: {context}")
# llm_chain = LLMChain(llm=OpenAI())

# doc_chain = StuffDocumentsChain(
#     document_variable_name=document_variable_name
# )

retriever = db.as_retriever(search_kwargs={"k": 3},search_type="similarity")

search_kwargs = {
    'k': 30,
    'fetch_k':100,
    'maximal_marginal_relevance': True,
    'distance_metric': 'cos',
}



# Modify the template to include page reference
template = """Combine the chat history and follow up question into a standalone question and answer the question at the end. 
If you don't know the answer, just say that you don't know, 
don't try to make up an answer. Chat History: {chat_history} Follow up question: {question}

"""
prompt = PromptTemplate.from_template(template)

prompt = ChatPromptTemplate.from_messages([
        ("system", """Answer the user's questions based on the context: {context}. Provide citations and page references and
         If you don't know the answer, just say that you don't know, don't try to make up an answer.
         """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

document_chain = create_stuff_documents_chain(
    llm=model,
    prompt=prompt
)

question_generator_chain = LLMChain(llm=OpenAI(), prompt=prompt)

memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer')



# Define Conversational Retrieval Chain
# chain = ConversationalRetrievalChain(
#     combine_docs_chain=document_chain,
#     retriever=db,
#     question_generator=question_generator_chain,
#     return_source_documents=True,
#     memory=memory,
#     response_if_no_docs_found="Sorry can't find anything on that topic"
# )

chain = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0.3), 
                                                  retriever=retriever,
                                                  return_source_documents=True,)


question = "What is cross-validation?"

# Invoke the chain with the input data
response = chain.invoke({"question": question, "chat_history": []})
doc = response['source_documents'][0].to_json()['kwargs']
print(doc['metadata']['page'])

