
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_answer(question, transcript_text):

    context = f"{transcript_text}\n\nQuestion: {question}\nAnswer:"

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {f"role": "user", "content": context}
        ]
    )

    # Extract response from completion
    response = completion.choices[0].message.content

    return response
