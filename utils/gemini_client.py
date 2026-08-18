import os
from dotenv import load_dotenv
from google import genai
from utils.prompts import SUMMARY_PROMPT
from utils.prompts import FLASHCARD_PROMPT
from utils.prompts import QUIZ_PROMPT

# reads .env file.
load_dotenv()

# os.getenv() gets the value of GEMINI_API_KEY
# genai.Client() creates a client that can send requests to Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_summary(text):
    prompt = SUMMARY_PROMPT.format(text=text)

    # API Call
    response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)

    return response.text


def generate_flashcards(text):
    # inserts the PDF text into the flashcard prompt
    prompt = FLASHCARD_PROMPT.format(text=text)

    response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)

    return response.text


def generate_quiz(text, difficulty):

    prompt = QUIZ_PROMPT.format(text=text, difficulty=difficulty)

    response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)

    return response.text
