import json
import os
import re
from utils.shared_memory import save_to_memory, read_memory
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv(dotenv_path="creds/gemini.env")

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

def handle_json(json_content,file_path):
    print("\n[JSON Agent Invoked]")

    
    memory = read_memory()
    print("Recent memory entries related to JSON:")
    for entry in memory.values():
        if entry.get("type") == "JSON":
            print(entry)

    # LLM Prompt
    prompt = f"""
    You are a JSON agent. Your task is to:
    1. Reformat this JSON into the target schema with these keys:
       - Invoice ID
       - Amount
       - Customer
       - Date
    2. Flag missing fields or anomalies.

    JSON Input:
    {json.dumps(json_content)}

    Respond only in JSON format.
    """

    response = llm.invoke([HumanMessage(content=prompt)]).content
    print("[Raw LLM Output]:", response)

    # Clean up response in case it's wrapped in triple backticks
    try:
        cleaned = re.sub(r"^```json|```$", "", response.strip()).strip()
        extracted = json.loads(cleaned)
    except json.JSONDecodeError:
        print("Failed to parse response as JSON.")
        extracted = {"error": "Invalid JSON", "raw": response}

    print("[Parsed Output]:", extracted)

    # Save to memory
    file_key = os.path.basename(file_path)
    save_to_memory(
        file_key=file_key,
        key="json_agent_output",
        value={
            "agent": "json_agent",
            "type": "JSON",
            "extracted": extracted
        }
    )


