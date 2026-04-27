from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

def call_llm(prompt):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content