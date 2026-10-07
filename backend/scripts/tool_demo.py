from google import genai

from app.core.config import settings
import json

from app.services.analyzer import analyze_text, analyze_kyrgyz_readability

client = genai.Client(api_key=settings.gemini_api_key)
MODEL = "gemini-3.5-flash-lite"

analyze_readability_tool = {
    "type": "function",
    "name": "analyze_readability",
    "description": (
        "Measures a Kyrgyz text: word, sentence and syllable counts, "
        "ARI score and a readability score."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "The Kyrgyz text to measure"},
        },
        "required": ["text"],
    },
}

question = (
    "Is this text suitable for a 7-year-old?\n\n"
    "Text: Таңкы мектепке барам. Мен китеп окуймун."
)

def run_tool(name: str, arguments: dict) -> dict:
    if name == "analyze_readability":
        text = arguments["text"]
        return {**analyze_text(text), **analyze_kyrgyz_readability(text)}
    return {"error": f"Unknown tool: {name}"}


interaction = client.interactions.create(
    model=MODEL,
    input=question,
    tools=[analyze_readability_tool],
)

print(interaction)

fc_step = next(s for s in interaction.steps if s.type == "function_call")

result = run_tool(fc_step.name, fc_step.arguments)
print("Tool result:", result)

final = client.interactions.create(
    model=MODEL,
    input=[
        {
            "type": "function_result",
            "name": fc_step.name,
            "call_id": fc_step.id,
            "result": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
        }
    ],
    tools=[analyze_readability_tool],
    previous_interaction_id=interaction.id,
)

print("Answer:", final.output_text)