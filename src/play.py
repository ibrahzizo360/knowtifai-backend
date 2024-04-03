from langchain_openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain.chains import StuffDocumentsChain, LLMChain, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Load PDF Documents
pdf_path = "./pdf/8.pdf"
loader = PyPDFLoader(pdf_path)
pages = loader.load_and_split()

# Create Vector Store and Retrieval System
embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(pages, OpenAIEmbeddings())
db = db.as_retriever()

# Define Prompt Templates and Chains
document_prompt = PromptTemplate(input_variables=["page_content"], template="{page_content}")
document_variable_name = "context"

prompt = PromptTemplate.from_template("Summarize this: {context}")
llm_chain = LLMChain(llm=OpenAI(), prompt=prompt)

doc_chain = StuffDocumentsChain(
    llm_chain=llm_chain,
    document_prompt=document_prompt,
    document_variable_name=document_variable_name
)

# Modify the template to include page reference
template = "Combine the chat history and follow up question into a standalone question. Chat History: {chat_history} Follow up question: {question}"
prompt = PromptTemplate.from_template(template)

question_generator_chain = LLMChain(llm=OpenAI(), prompt=prompt)

memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer')



# Define Conversational Retrieval Chain
chain = ConversationalRetrievalChain(
    combine_docs_chain=doc_chain,
    retriever=db,
    question_generator=question_generator_chain,
    return_source_documents=True,
    memory=memory,
)


question = "What's my name?"

# Invoke the chain with the input data
response = chain.invoke({"question": question})
print(response)

