import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

from utils.shared_memory import save_to_memory, get_full_memory
from agents.email_agent import handle_email
from agents.json_agent import handle_json
from utils.file_loader import load_file_format, read_content

from dotenv import load_dotenv

load_dotenv(dotenv_path="creds/gemini.env")

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

def classify_and_route(file_path):
    format = load_file_format(file_path)
    content = read_content(file_path)
    filename = os.path.basename(file_path)

    prompt = f"""
    Classify the format and intent of the following message:

    Content:
    {content}

    Respond in JSON with fields "format" and "intent".
    """

    response = llm.invoke([HumanMessage(content=prompt)]).content
    print("[Classifier Response]", response)

    # Fallback parsing (since response may not be strict JSON)
    if format.lower() == "pdf":
        format_detected = "PDF"
    else:
        format_detected = None
        if "email" in response.lower():
            format_detected = "Email"
        elif "json" in response.lower():
            format_detected = "json"

    summary = None
    if format_detected == "PDF":
        print("PDF detected. Generating summary...")
        summary_prompt = f"""
        Summarize the following PDF content in 3-4 bullet points for quick CRM reference:

        Content:
        {content[:3000]}  # limit to prevent token overload
        """
        summary = llm.invoke([HumanMessage(content=summary_prompt)]).content
        print("[PDF Summary]", summary)
        save_to_memory(filename, "summary", summary)

    if "invoice" in response.lower():
        intent = "Invoice"
    elif "rfq" in response.lower():
        intent = "RFQ"
    elif "complaint" in response.lower():
        intent = "Complaint"
    elif "regulation" in response.lower():
        intent = "Regulation"
    else:
        intent = "Unknown"

    print("[Detected Format]", format_detected)
    print("[Detected Intent]", intent)

    # Save classification result to memory
    save_to_memory(filename, "source", file_path)
    save_to_memory(filename, "type", format_detected)
    save_to_memory(filename, "intent", intent)
    save_to_memory(filename, "content", content[:300])

    # Route to correct agent
    if format_detected == "Email":
        routing_result = handle_email(content, file_path)
    elif format_detected == "json":
        routing_result = handle_json(content, file_path)
    else:
        print("No handler yet for format:", format_detected)
        routing_result = f"No handler for format: {format_detected}"

    return {
        "filename": filename,
        "format_detected": format_detected,
        "intent": intent,
        "classifier_response": response,
        "summary": summary,
        "routing_result": routing_result
    }

if __name__ == "__main__":
    input_folder = "input_samples"
    all_results = []

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)

        if os.path.isfile(file_path):
            print(f"\nProcessing: {filename}")
            result = classify_and_route(file_path)
            all_results.append(result)

    print("\n=== Final Aggregated Results ===")
    for r in all_results:
        print(f"\nFile: {r['filename']}")
        print("Format:", r['format_detected'])
        print("Intent:", r['intent'])
        print("Classifier Response:", r['classifier_response'])
        print("Summary:", r['summary'])
        print("Routing Result:", r['routing_result'])
