import os
import json
import mimetypes
import fitz  # PyMuPDF

def load_file_format(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if "pdf" in mime_type:
            return "PDF"
        elif "json" in mime_type:
            return "JSON"
        elif "plain" in mime_type or file_path.endswith(".txt"):
            return "Email"
    return "Unknown"

def read_content(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".json"):
        with open(file_path, 'r') as f:
            return f.read()
    elif file_path.endswith(".txt"):
        with open(file_path, 'r') as f:
            return f.read()
    else:
        return "Unsupported file format"



def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text
