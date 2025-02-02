import os
import re

from dotenv import load_dotenv
from openai import OpenAI

from src.agents.reporter.prompts import DEFAULT_SYSTEM_PROMPT

load_dotenv()

DEFAULT_MODEL = "gpt-4o-mini"

client = OpenAI(
    organization=os.getenv("OPENAI_ORGANIZATION"),
    project=os.getenv("OPENAI_PROJECT"),
    api_key=os.getenv("OPENAI_API_KEY"),
)


def generate_completion(data: str, introduction: str) -> str:
    prompt = DEFAULT_SYSTEM_PROMPT
    prompt = re.sub(r"{introduction}", introduction, prompt)
    prompt = re.sub(r"{data}", data, prompt)

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=2000,
    )
    return response.choices[0].message.content
