from google import genai

from app.core.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Say hello in Kyrgyz and explain in one sentence what you said.",
)

print(response.text)