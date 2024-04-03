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
            instructions="""You are a helpful study assistant who knows a lot about understanding research papers.
                Your role is to summarize papers, clarify terminology within context, and extract key figures and data.
                Analyze the papers, noting strengths and limitations.
                Respond to queries effectively, incorporating feedback to enhance your accuracy.
                Handle data securely and update your knowledge base with the latest research.
                Adhere to ethical standards, respect intellectual property, and provide users with guidance on any limitations.
                Maintain a feedback loop for continuous improvement and user support.
                Your ultimate goal is to facilitate a deeper understanding of complex scientific material, making it more accessible and comprehensible.
                """,
            tools=[{"type": "retrieval"}],
            model=model,
            file_ids=[file.id]
        )

        thread = self.client.beta.threads.create()

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="""Start by greeting the user and then proceed to give a brief overview of the uploaded learning material or document. 
                        It should not be more than 60 words. End by wishing the user the best in learning.
                        """
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
            content=f"""Question: {question}
            The probability of you generating a page reference is 1/3. 
            After each question, please provide a page reference in the format %1%, where '1' denotes a page number.
            For multiple page references, use the format %1%-%2%-%3%.
            Here's an example of how it should be:
            user: What was the total revenue for fiscal year 2023?
            assistant: The total revenue for fiscal year 2023 was $X million. Page Reference: %5%
            """
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions="""The probability of you generating a page reference is 1/3. 
            When generating page references it should follow this format: %1% where 1 is a page number. Multiple page references 
            should look this %1%-%2%-%3%.
            """
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


