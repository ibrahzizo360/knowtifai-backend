
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
        ],
        max_tokens=200,
    )

    response = completion.choices[0].message.content

    return response


def generate_summary(transcript_text):

    context = f"""Can you provide a comprehensive summary of the given trancript of a lecture video? The summary should cover all the key points
    and main ideas presented in the original text, while also condensing the information into a concise and easy-to-understand
    format. Please ensure that the summary includes relevant details and examples that support the main ideas, while avoiding any
    unnecessary information or repetition. The length of the summary should be appropriate for the length and complexity of the 
    original text, providing a clear and accurate overview without omitting any important information.
    ###
    transcription text: {transcript_text}"""

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {f"role": "user", "content": context}
        ],
        max_tokens=200,
    )

    response = completion.choices[0].message.content

    return response