from groq import Groq
import os

# Initialize client safely
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def call_llm(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise and structured AI assistant. "
                        "Always follow the requested format strictly. "
                        "Avoid unnecessary explanations."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,   # 🔥 more stable outputs
            max_tokens=800
        )

        content = response.choices[0].message.content

        # Safety check
        if not content or not content.strip():
            return "⚠️ Empty response from AI. Please try again."

        return content.strip()

    except Exception as e:
        return (
            "⚠️ AI service is temporarily unavailable.\n"
            "Please try again in a moment."
        )