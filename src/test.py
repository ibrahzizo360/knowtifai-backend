import json

import requests

# url = "http://localhost:8000/chat"
# message = "what is glucose?"
# data = {"message": message, "session_id": "cat-conversation"}

# headers = {"Content-type": "application/json"}

# with requests.post(url, data=json.dumps(data), headers=headers, stream=True) as r:
#     for line in r.iter_lines():
#         if line:
#             print(line.decode('utf-8'), flush=True)
#             # data = json.loads(line)
#             # print(data)


query = "What is regularization in machine learning? How does it work? What are the different types of regularization techniques?"
data = {"question": "Write a python code to print the first 10 numbers in the fibonacci sequence."}

url = f'http://127.0.0.1:8000/v2/get_answers'

with requests.post(url,data=json.dumps(data), stream=True) as r:
    for chunk in r.iter_content(1024): 
        print(chunk.decode('utf-8'), end="")