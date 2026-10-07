from app.services.assistant import ask_assistant

text = "Таңкы мектепке барам. Мен китеп окуймун."

for question in [
    "Is this text suitable for a 7-year-old?",
    "What is the capital of France?",
]:
    result = ask_assistant(text, question)
    print("Q:", question)
    print("Answer:", result["answer"])
    print("Tools used:", result["tools_used"])
    print("-" * 40)