import os
from google import genai
from google.genai import types

# Load your markdown context
with open("advisory_board_agent.md", "r") as f:
    instructions = f.read()

with open("company_context.md", "r") as f:
    company_context = f.read()

with open("board_memory.md", "r") as f:
    memory = f.read()

system_prompt = f"{instructions}\n\n=== COMPANY CONTEXT ===\n{company_context}\n\n=== SESSION MEMORY ===\n{memory}"

client = genai.Client()

chat = client.chats.create(
    model="gemini-2.5-pro",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7,
    )
)

print("QuickStart Marketing Advisory Board Online. Ask a question or submit an asset:")
while True:
    user_input = input("\nYou: ")
    if user_input.strip().lower() in ["exit", "quit"]:
        break
    response = chat.send_message(user_input)
    print(f"\n{response.text}")