import os
import uvicorn
import json
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from a .env file in the project root
load_dotenv()

# --- Configuration ---
LLM_MODEL_NAME = "gemini-1.5-flash"

# --- FastAPI App ---
app = FastAPI(title="LLM Vulnerability Analyst API")

# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    question: str
    vulnerabilities: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    answer: str

# --- Helper Functions ---
def get_gemini_api_key():
    """Retrieves the Gemini API key from environment variables."""
    api_key = os.getenv("GOOGLE_API_KEY_3")
    if not api_key:
        # In a real application, you might want to handle this more gracefully
        raise ValueError("GOOGLE_API_KEY_3 not found in .env file or environment variables.")
    return api_key

def build_llm_prompt(question: str, vulnerability_data: Dict[str, Any]) -> str:
    """
    Constructs a detailed, single prompt for the LLM to analyze the vulnerability data.
    """
    return f"""
    As an expert cybersecurity data analyst, your task is to answer the user's question based on the provided JSON vulnerability data. Your answer must be clear, concise, well-formatted, and directly address the user's query.

    **Key Fields Reference:**
    - `cve_id`: The unique identifier for a vulnerability.
    - `cvss_score`: The severity score from 0.0 to 10.0. Higher is more severe. (Critical: 9.0-10.0, High: 7.0-8.9, Medium: 4.0-6.9).
    - `ranking`: An internal ranking score. Lower is more critical. This should be the primary field for sorting "top" or "most critical" vulnerabilities.
    - `service_name`: The network service (e.g., 'ssh', 'http') where the vulnerability was found.
    - `package`: The software package that is vulnerable.
    - `fixed_version`: The version of the package that patches the vulnerability.

    **Output Style Guide:**
    - Adopt a helpful, clear, and professional tone. Avoid overly technical jargon where possible.
    - When listing vulnerabilities, present them in a narrative style rather than a dry list of fields.
    - **Example of desired output format for a top vulnerability:** 
      "The most critical vulnerability is **CVE-2017-5638** (CVSS: 9.8), a critical remote code execution flaw in the `Apache Tomcat` service found on host `10.10.1.12`."

    **JSON Data Context:**
    ```json
    {json.dumps(vulnerability_data, indent=2)}
    ```

    **User's Question:**
    {question}

    **Instructions:**
    - Analyze the JSON data above to formulate your answer.
    - When asked for "top" or "most critical" vulnerabilities, you MUST sort the vulnerabilities by the `ranking` field in ascending order.
    - When asked "how many" vulnerabilities of a certain severity, you MUST count them based on their `cvss_score` and the severity ranges provided in the Key Fields Reference.
    - If the user's question cannot be answered from the data, state that clearly and explain what information is missing.
    - Present your answer clearly. Use markdown for lists and bolding to highlight key information.
    """

# --- API Endpoints ---
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Receives a question and vulnerability data, sends it to the LLM for analysis,
    and returns the answer.
    """
    # Guard clause: If no vulnerability data is provided, return a helpful message.
    if not request.vulnerabilities or not any(request.vulnerabilities.values()):
        return {"answer": "I'm ready to help! Please upload and analyze a scan file first, and then you can ask me questions about the results."}

    print(f"Received question: '{request.question}' with vulnerabilities: Yes")

    try:
        # Configure the generative AI model
        api_key = get_gemini_api_key()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(LLM_MODEL_NAME)

        # Build the prompt
        prompt = build_llm_prompt(request.question, request.vulnerabilities)
        
        # --- LLM Interaction Logging ---
        print("\n" + "="*50)
        print("--- Sending Prompt to LLM ---")
        print(prompt)
        print("="*50 + "\n")
        # --------------------------------

        # Generate the response from the LLM
        response = model.generate_content(prompt)
        answer = response.text

        # --- LLM Interaction Logging ---
        print("\n" + "="*50)
        print("--- Received Response from LLM ---")
        print(answer)
        print("="*50 + "\n")
        # --------------------------------

    except Exception as e:
        print(f"LLM API call error: {e}")
        answer = "I'm sorry, an error occurred while I was thinking. Please check my server logs and ensure the API key is valid."

    print(f"Generated answer: {answer}")
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 