# from fastapi import FastAPI
# from fastapi.responses import StreamingResponse
# from langchain.prompts import PromptTemplate
# from pydantic import BaseModel
# from langchain_community.vectorstores import MongoDBAtlasVectorSearch
# from langchain_openai import OpenAIEmbeddings
# from typing import AsyncGenerator
# import os
# from langchain.chains import create_retrieval_chain,RetrievalQAWithSourcesChain,ConversationalRetrievalChain
# from langchain.callbacks import AsyncIteratorCallbackHandler
# from langchain.callbacks.base import BaseCallbackHandler
# from langchain.schema.messages import BaseMessage

# from typing import Dict, List, Any
# import asyncio
# from threading import Thread
# from queue import Queue
# from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv
# from fastapi.middleware.cors import CORSMiddleware
# streamer_queue = Queue()
        
# app = FastAPI(
#     title="QA Chatbot Streaming using FastAPI, LangChain Expression Language , OpenAI, and Chroma",
#     version="0.1.0",
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# db = MongoDBAtlasVectorSearch.from_connection_string(
#     os.getenv('MONGO_URL'),
#     'embeddings.embeddings',
#     OpenAIEmbeddings(disallowed_special=()),
#     index_name='vector_index',
# )

# my_handler = MyCustomHandler(streamer_queue)
# chain_handler = ChainHandler()


# retriever = db.as_retriever(search_kwargs={"k": 6})
    
# streaming_llm = ChatOpenAI(
#         max_retries=15,
#         temperature=0.3,
#         callbacks=[my_handler],
#         streaming=True,
#     )
    
    
# chain = ConversationalRetrievalChain.from_llm(llm=streaming_llm, 
#                                                   retriever=retriever,
#                                                   return_source_documents=True,)
# def generate(query):
#     chain.invoke({"question": query, "chat_history": []},{"callbacks":[chain_handler]})


# def start_generation(query):
#     # Creating a thread with generate function as a target
#     thread = Thread(target=generate, kwargs={"query": query})
#     # Starting the thread
#     thread.start()


# async def response_generator(query):
#     # Start the generation process
#     start_generation(query)

#     # Starting an infinite loop
#     while True:
#         # Obtain the value from the streamer queue
#         value = streamer_queue.get()
#         # Check for the stop signal, which is None in our case
#         if value == None:
#             # If stop signal is found break the loop
#             break
#         # Else yield the value
#         yield value
#         # statement to signal the queue that task is done
#         streamer_queue.task_done()

#         # guard to make sure we are not extracting anything from 
#         # empty queue
#         await asyncio.sleep(0.1)
        
        
# async def generate_response(
#     question: str,
# ) -> AsyncGenerator[str, None]:

#     retriever = db.as_retriever(search_kwargs={"k": 6})
    
#     streaming_llm = ChatOpenAI(
#             max_retries=15,
#             temperature=0.3,
#             callbacks=[my_handler],
#             streaming=True,
#         )
    
    
#     chain = ConversationalRetrievalChain.from_llm(llm=streaming_llm, 
#                                                   retriever=retriever,
#                                                   return_source_documents=True,)


#     response = ""
#     async for token in chain.astream({"chat_history": [], "question": message}):  # type: ignore
#         print(token['answer'])
#         yield token['answer']
#         response += token['answer']



# @app.post("/chat")
# async def chat(
#     request: ChatRequest,
# ) -> StreamingResponse:
#     return StreamingResponse(
#         generate_response(
#             context="",
#             message=request.message,
#         ),
#         media_type="text/plain",
#     )

# @app.get('/query-stream/')
# async def stream(query: str):
#     print(f'Query receieved: {query}')
#     return StreamingResponse(response_generator(query), media_type='text/event-stream')



# # async def generator(question):
# #     run = asyncio.create_task(chain.acall({"question": question, "chat_history": []}))
    
# #     async for token in callback.aiter():
# #         print(token)
# #         yield token

# #     await run
    

# # # Conversation Route
# # @app.post('/conversation',status_code=200)
# # async def get_conversation(body: ChatRequest):
# #     question = body.message
# #     return StreamingResponse(generator(question), media_type="text/event-stream")
    
# # Uncomment if you want to run the FastAPI application
# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app)

