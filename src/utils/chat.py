
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

    response = completion.choices[0].message

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

    response = completion.choices[0].message

    return response

def generate_quiz(transcript_text):

    context = f"""Can you generate a quiz based on the given transcript of a lecture video? The quiz should include a variety of questions
    that test the reader's understanding of the main ideas and key details presented in the original text. Please ensure that the questions
    are clear, accurate, and relevant to the content of the transcript, covering a range of topics and concepts to provide a comprehensive
    assessment of the reader's knowledge. The quiz should include multiple-choice, true/false, and short answer questions, with a suitable
    number of questions for the length and complexity of the original text. Please also provide answer keys for the quiz at the end of everything, including
    explanations and additional information where necessary. After each question, add the text %new% to indicate the start of a new question.
    
    transcription text: {transcript_text}"""

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {f"role": "user", "content": context}
        ],
        max_tokens=800,
    )

    response = completion.choices[0].message

    return response