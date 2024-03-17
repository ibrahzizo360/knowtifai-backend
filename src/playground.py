from utils.chat import client

model = 'gpt-3.5-turbo-16k'

# assistant = client.beta.assistants.create(
#     name = 'study_buddy',
#     instructions = """You are an excellent study partner. You've helped tons of students understand everything they want to learn.
#     You will be given a pdf so that you reference it to answer the questions the user throws at you.""",
#     model = model
# )

# assistant_id = assistant.id
# print(assistant_id)

# thread = client.beta.threads.create(
#     messages = [
#         {
#             "role": "user",
#             "content": "Who are you?"
#         }
#     ]
# )

# thread_id = thread.id

# print(thread_id)


class AssistantManager:
    thread_id: None
    assistant_id: None

    def __init__(self, model: str = model, ) -> None:
        self.client = client
        self.assistant = None
        self.thread = None
        self.run = None
        self.answer = None

        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id = AssistantManager.assistant_id
            )

        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id = AssistantManager.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            self.assistant = self.client.beta.assistants.create(
                name = name,
                instructions = instructions,
                tools = tools
            )
            AssistantManager.assistant_id = self.assistant.id
            print(f"AsistantID::: {self.assistant.id}")       
        
    def create_thread(self):
        if not AssistantManager.thread_id:
            self.thread = self.client.beta.threads.create()
            AssistantManager.thread_id = self.thread.id
            print(f"ThreadId::::: {self.thread.id}")

    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id = self.thread.id,
                role = role,
                content = content
            )        

    def run_assistant(self, instructions):
        if self.thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id = self.thread.id,
                assistant_id = self.assistant.id,
                instructions= instructions
            )        