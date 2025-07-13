import os
import google.generativeai as genai
from typing import Dict, Any
import json
from dotenv import load_dotenv
import traceback
from datetime import date

# Load environment variables from .env file
load_dotenv()

# --- PLACEHOLDER ---
# Please create a .env file in the root of the project and add your API key:
# GOOGLE_API_KEY_2="YOUR_API_KEY_HERE"
API_KEY = os.getenv("GOOGLE_API_KEY_2")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        print(f"Error configuring Generative AI: {e}")
        traceback.print_exc()

MODEL_NAME = 'gemini-1.5-flash'
GENERATION_CONFIG = {
    "temperature": 0.2,
}

def _get_severity_text(score: float) -> str:
    """Converts a CVSS score to a human-readable severity level."""
    if score >= 9.0:
        return "Critical"
    elif score >= 7.0:
        return "High"
    elif score >= 4.0:
        return "Medium"
    else:
        return "Low"

def generate_executive_summary(vulnerability_data: Dict[str, Any]) -> str:
    """
    Generates a formal Internal Security Advisory for business stakeholders.
    """
    print("\n--- Received request to generate formal security advisory ---")
    if not API_KEY:
        print("API Key not configured. Aborting.")
        return "Error: GEMINI_API_KEY not configured."

    prompt_template = """
    You are a Director of Cybersecurity creating a formal **Internal Security Advisory** for business leaders and stakeholders.
    Based on the JSON data provided, generate a comprehensive but non-technical advisory using Markdown.

    **Instructions:**
    - The tone must be professional, authoritative, and clear.
    - Adhere strictly to the report structure and headings provided below.
    - Do not use technical jargon. Explain concepts in terms of business risk.

    **Report Structure:**

    # Internal Security Advisory: {cve_id}

    - **Advisory ID:** VULN-{year}-{cve_id_num}
    - **Date Issued:** {current_date}
    - **Severity Level:** {severity_text}
    - **Status:** Action Required

    ### 1. Executive Overview
    A **{severity_text}** severity security vulnerability, identified as **{cve_id}**, has been confirmed within our environment. This vulnerability affects the **{service_name}** service, which is integral to our **[Infer the business function, e.g., 'Remote Access Infrastructure', 'Public Web Services', 'Database Operations']**. Due to its high exploitability and potential for significant disruption, immediate attention and remediation are required.

    ### 2. Business Impact Analysis
    If exploited, this vulnerability could have a material impact on the business across several domains:
    - **Strategic Risk:** An attack could undermine customer trust and damage our brand reputation, potentially impacting long-term growth and market position.
    - **Financial Risk:** The direct costs of remediation, potential regulatory fines (if data is breached), and revenue loss from service downtime could be substantial.
    - **Operational Risk:** The **{service_name}** service could be rendered inoperable, leading to significant disruption of daily business activities and employee productivity that rely on this service.
    - **Reputational Risk:** A public security incident could lead to negative press coverage and a loss of confidence from customers and partners.

    ### 3. Affected Business Services
    Based on our initial assessment, the primary business function at risk is our **[Infer the business function again]**. All departments and personnel who utilize the **{service_name}** for their operations are considered impacted.

    ### 4. High-Level Remediation Plan
    The cybersecurity team has initiated a formal response process, structured in three phases:
    1.  **Phase 1: Immediate Containment (In Progress):** We are implementing temporary safeguards to reduce the immediate risk of exploitation while a permanent solution is prepared.
    2.  **Phase 2: Scheduled Patching (Pending):** A permanent security patch will be deployed across all affected systems. This will be scheduled in coordination with business units to minimize operational disruption.
    3.  **Phase 3: Verification and Monitoring (Post-Patching):** After deployment, we will conduct rigorous testing to confirm the vulnerability is resolved and will continue to monitor the systems for any unusual activity.

    ### 5. Next Steps
    Stakeholders are not required to take any technical action at this time. A follow-up communication will be sent once the patching schedule is finalized. For any immediate concerns regarding business operations, please contact the IT Help Desk.

    **Vulnerability Data Reference:**
    ```
    {vulnerability_data}
    ```
    """

    try:
        print("Initializing GenerativeModel for formal advisory...")
        model = genai.GenerativeModel(MODEL_NAME)
        
        cvss_score = vulnerability_data.get('cvss_score', 0.0)
        cve_id = vulnerability_data.get('cve_id', 'N/A')
        
        prompt = prompt_template.format(
            cve_id=cve_id,
            year=date.today().year,
            cve_id_num=cve_id.split('-')[-1] if cve_id != 'N/A' else '0000',
            current_date=date.today().strftime("%B %d, %Y"),
            severity_text=_get_severity_text(cvss_score),
            service_name=vulnerability_data.get('service_name', 'an internal service'),
            vulnerability_data=json.dumps(vulnerability_data, indent=2)
        )

        print("Calling Gemini API to generate formal advisory...")
        response = model.generate_content(prompt, generation_config=GENERATION_CONFIG)
        print("Successfully received response from Gemini API for formal advisory.")
        return response.text
    except Exception as e:
        print(f"An error occurred while generating the executive summary: {e}")
        traceback.print_exc()
        return "Error: Could not generate the executive summary."


def generate_technical_report(vulnerability_data: Dict[str, Any]) -> str:
    """
    Generates a structured technical report for a single vulnerability using an LLM.
    """
    print("\n--- Received request to generate technical report ---")
    if not API_KEY:
        print("API Key not configured. Aborting.")
        return "Error: GEMINI_API_KEY not configured."

    prompt_template = """
    You are a senior security engineer creating a technical remediation report for a system administrator.
    Based on the JSON vulnerability data, generate a detailed report using Markdown.

    **Instructions:**
    - Use Markdown headings (##) for each section.
    - Use bullet points for lists and bold text for labels.
    - Use code blocks for commands or version identifiers.

    **Report Structure:**

    # Technical Report: {cve_id}

    ## 1. Vulnerability Details
    - **CVE ID:** {cve_id}
    - **Description:** A remote code execution vulnerability exists in Apache Struts. An attacker can exploit this by sending a crafted request with a malicious 'Content-Type' header.
    - **CVSS Score:** {cvss_score} (Critical)
    - **Exploitability Score:** {exploitability_score}

    ## 2. Affected Systems
    - **Host IP:** {host_ip}
    - **Operating System:** {os}
    - **Affected Service:** {service_name} on port {port}
    - **Affected Version:** {version}

    ## 3. Remediation Steps
    1.  **Isolate the Host:** Immediately limit network access to the affected host at **{host_ip}** to prevent exploitation.
    2.  **Upgrade the Package:** The vulnerability is patched in a later version. The fixed version identifier is:
        ```
        {fixed_version}
        ```
        You must upgrade the 'Apache Tomcat' package to a version that includes this fix or a more recent one.
    3.  **Verify the Fix:** After applying the update, confirm that the service is running correctly and that the version has been successfully updated.

    **Vulnerability Data Used:**
    ```
    {vulnerability_data}
    ```
    """

    try:
        print("Initializing GenerativeModel for technical report...")
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = prompt_template.format(
            cve_id=vulnerability_data.get('cve_id', 'N/A'),
            cvss_score=vulnerability_data.get('cvss_score', 'N/A'),
            exploitability_score=vulnerability_data.get('exploitability_score', 'N/A'),
            host_ip=vulnerability_data.get('host_ip', 'N/A'),
            os=vulnerability_data.get('os', 'N/A'),
            port=vulnerability_data.get('port', 'N/A'),
            service_name=vulnerability_data.get('service_name', 'N/A'),
            version=vulnerability_data.get('version', 'N/A'),
            fixed_version=vulnerability_data.get('fixed_version', 'Not specified.'),
            vulnerability_data=json.dumps(vulnerability_data, indent=2)
        )
        
        print("Calling Gemini API to generate technical report...")
        response = model.generate_content(prompt, generation_config=GENERATION_CONFIG)
        print("Successfully received response from Gemini API for technical report.")
        return response.text
    except Exception as e:
        print(f"An error occurred while generating the technical report: {e}")
        traceback.print_exc()
        return "Error: Could not generate the technical report."
