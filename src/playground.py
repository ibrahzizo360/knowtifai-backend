from utils.chat import client

model = 'gpt-3.5-turbo-16k'

assistant = client.beta.assistants.create(
    name = 'study_buddy',
    instructions = """You are an excellent study partner. You've helped tons of students understand everything they want to learn.
    You will be given a pdf so that you reference it to answer the questions the user throws at you.""",
    model = model
)

assistant_id = assistant.id
print(assistant_id)

thread = client.beta.threads.create(
    messages = [
        {
            "role": "user",
            "content": "Who are you?"
        }
    ]
)

thread_id = thread.id

print(thread_id)


class AssitantManager:
    thread_id: None
    assistant_id: None

    def __init__(self) -> None:
        pass