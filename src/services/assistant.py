from utils.chat import client
import time
from typing import List
model = 'gpt-3.5-turbo'

class AssistantManager:

    def __init__(self, model: str = model, ) -> None:
        self.client = client
        self.assistant = None
        self.thread = None         
    
    def upload_file(self, file_path: str):
        """
        Uploads a file to the OpenAI API and creates an assistant related to that file.

        Args:
            filename (str): The path to the file to be uploaded.
        """
        file = self.client.files.create(
            file=file_path,
            purpose="assistants",
        )

        assistant = self.client.beta.assistants.create(
            name="PDF Helper",
            instructions="You are my assistant who can answer questions from the given pdf",
            tools=[{"type": "retrieval"}],
            model=model,
            file_ids=[file.id]
        )

        thread = self.client.beta.threads.create()

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Start by greeting the user and then proceed to give a brief overview of the uploaded learning material or document. It should not be more than 60 words. End by wishing the user the best in learning."
        )

        while True:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            time.sleep(5)
            if run_status.status == 'completed':
                messages = self.client.beta.threads.messages.list(thread_id=thread.id)
                break
            else:
                time.sleep(2)

        message = [message.content[0] for message in messages.data if message.role == "assistant"]
        
        return {
            "assistant_id": assistant.id,
            "thread_id": thread.id,
            "message": message,
        }

    def get_answers(self, question: str, assistant_id: str, thread_id: str) -> List[str]:
        """
        Asks a question to the assistant and retrieves the answers.

        Args:
            question (str): The question to be asked to the assistant.

        Returns:
            List[str]: A list of answers from the assistant.

        Raises:
            ValueError: If the assistant has not been created yet.
        """
        

        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=question
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        while True:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            time.sleep(5)
            if run_status.status == 'completed':
                messages = self.client.beta.threads.messages.list(thread_id=thread_id)
                break
            else:
                time.sleep(2)

        return [message.content[0] for message in messages.data if message.role == "assistant"]    