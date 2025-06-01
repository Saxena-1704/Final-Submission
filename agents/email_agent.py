import json
import os
from utils.shared_memory import save_to_memory, read_memory
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import re
from dotenv import load_dotenv

load_dotenv(dotenv_path="creds/gemini.env")

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

#  Use Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

def handle_email(email_content,file_path):
    print("\n[Email Agent Invoked]")

    # Access shared memory and display recent email entries
    memory = read_memory()
    print("Recent memory entries related to email:")
    for entry in memory.values():
        if entry.get("type") == "Email":
            print(entry)

    # LLM prompt for current email
    prompt = f"""
    You are an email agent. Extract the following from this email:
    - Sender
    - Subject
    - Intent (Invoice, Complaint, RFQ, etc.)
    - Urgency (Low, Medium, High)
    - Message Summary(cannot be null)
    - Requires Response (Yes, No)
    
    Email:
    {email_content}

    Respond only in JSON format.
    """

    response = llm.invoke([HumanMessage(content=prompt)]).content
    print("[Raw LLM Output]:", response)

    try:
        # Remove triple backticks and 'json' if present
        cleaned = re.sub(r"^```json|```$", "", response.strip()).strip()
        extracted = json.loads(cleaned)
    except json.JSONDecodeError:
        print("Failed to parse response as JSON.")
        extracted = {"error": "Invalid JSON", "raw": response}
    
    print("[Parsed Output]:", extracted)

    # Save to shared memory
    file_key = os.path.basename(file_path)  # or just use file_path if unique
    save_to_memory(
    file_key=file_key,
    key="email_agent_output",
    value={
        "agent": "email_agent",
        "type": "Email",
        "extracted": extracted
    }
    )




