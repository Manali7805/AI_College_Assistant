import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_ai(prompt):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def ask_from_data(data, question):
    prompt = f"""
You are a smart college assistant.

Make answers attractive using emojis 🎉📊🏆.

DATA:
{data}

QUESTION:
{question}
"""
    return ask_ai(prompt)

def generate_image(prompt):
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    image_base64 = response.data[0].b64_json
    return base64.b64decode(image_base64)