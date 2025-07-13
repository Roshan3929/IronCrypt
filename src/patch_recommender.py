import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Configure the generative AI model
try:
    api_key = os.environ.get("GOOGLE_API_KEY4")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY4 environment variable not set.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error configuring Generative AI: {e}")
    model = None

# In-memory cache for recommendations
recommendation_cache = {}

def get_patch_recommendation(vulnerability_details: dict, playbook_content: Optional[str] = None) -> str:
    """
    Generates a patch recommendation for a given vulnerability using a generative AI model.
    Caches results to avoid redundant API calls.

    Args:
        vulnerability_details: A dictionary containing details about the vulnerability.
        playbook_content: A string containing the content of the patch.yml file.

    Returns:
        A string containing the patch recommendation, or an error message.
    """
    if not model:
        return "Error: Generative AI model not initialized. Check API key and configuration."

    # Create a unique cache key for the vulnerability + playbook content
    cache_key = (vulnerability_details.get('cve_id') or str(vulnerability_details)) + (playbook_content or "")
    if cache_key in recommendation_cache:
        return recommendation_cache[cache_key]

    # Construct the prompt for the LLM
    playbook_context_prompt = ""
    if playbook_content:
        playbook_context_prompt = f"""
        Here is the current Ansible playbook (`patch.yml`) for context. The tasks in this playbook represent patches that can be deployed.
        ---
        {playbook_content}
        ---
        """

    prompt = f"""
    Based on the following vulnerability data and the provided Ansible playbook, please provide a concise and actionable patch recommendation.
    The recommendation should ideally leverage the existing playbook if a relevant task exists. If not, suggest a new Ansible task to fix the vulnerability.

    Vulnerability Details:
    - CVE ID: {vulnerability_details.get('cve_id', 'N/A')}
    - Description: {vulnerability_details.get('description', 'N/A')}
    - CVSS v3 Score: {vulnerability_details.get('cvss_v3_score', 'N/A')}
    - Severity: {vulnerability_details.get('cvss_v3_severity', 'N/A')}
    - Affected CPEs: {', '.join(vulnerability_details.get('cpes', []))}

    {playbook_context_prompt}

    Please provide the patch recommendation:
    """

    try:
        response = model.generate_content(prompt)
        recommendation = response.text.strip()
        
        # Cache the successful recommendation
        recommendation_cache[cache_key] = recommendation
        
        return recommendation
    except Exception as e:
        return f"Error generating recommendation: {str(e)}"


def generate_ansible_playbook(vulnerability_data: dict) -> str:
    """
    Generates a full Ansible playbook from a dictionary of vulnerabilities.

    Args:
        vulnerability_data: The full vulnerability data object.

    Returns:
        A string containing the generated Ansible playbook in YAML format, or an error message.
    """
    if not model:
        return "Error: Generative AI model not initialized. Check API key and configuration."

    # Prepare a condensed version of the vulnerability data for the prompt
    vuln_summary = []
    for host_ip, host_data in vulnerability_data.items():
        for service in host_data.get('services', []):
            for vuln in service.get('vulnerabilities', []):
                vuln_summary.append(
                    f"- Host: {host_ip}, Package: {vuln.get('package', 'N/A')}, "
                    f"CVE: {vuln.get('cve_id', 'N/A')}, Details: {vuln.get('description', 'N/A')}"
                )
    
    # New, detailed prompt from the user
    user_prompt = """
I have an Ansible playbook that patches various CVEs on specific IP-based hosts. I want you to help me refactor and improve it to follow best practices. Here's what I need:

Consolidate repetitive tasks into a cleaner, scalable structure.
Replace raw IPs with hostnames and move host management to an inventory file.
Add logic to handle different OS types (e.g., Debian vs RHEL) using ansible_os_family.
Use variables (like dictionaries) to define which packages should be patched on which hosts.
Replace placeholder package names (like "*microsoft*") with actual packages if known.
Show a debug message when there's no patch defined for a host.
Add result tracking using register and debug so I can verify patch status.
Add conditional service restarts or reboots if patches are applied.
Use meaningful tags (security, patching, reboot, etc.) to filter task execution.
Include comments and good task naming for readability.
Add logging or output options for audit purposes.
Modularize the logic using roles if possible, for reusability.
Secure any credentials or sensitive data using ansible-vault (if applicable).
Give me a complete, production-quality version of this playbook with all the above improvements applied. Also include the inventory structure if needed.
"""

    prompt = f"""
You are an expert Ansible automation engineer. Your task is to generate a production-quality Ansible playbook and an associated inventory file based on a list of vulnerabilities.

Please follow these detailed instructions to create the playbook:
{user_prompt}

Here is the list of vulnerabilities you need to create patches for:
{chr(10).join(vuln_summary)}

Based on this data, please generate the complete playbook and inventory file. The output should be a single block of text containing valid YAML. 
Crucially, you must clearly separate the inventory from the playbook using the following markers on their own lines:
# --- INVENTORY ---
(inventory content goes here)
# --- PLAYBOOK ---
(playbook content goes here)
"""

    try:
        response = model.generate_content(prompt)
        # Clean up the response to ensure it's valid YAML
        playbook_yaml = response.text.strip()
        if playbook_yaml.startswith('```yaml'):
            playbook_yaml = playbook_yaml[7:]
        if playbook_yaml.endswith('```'):
            playbook_yaml = playbook_yaml[:-3]
        
        return playbook_yaml.strip()
    except Exception as e:
        return f"Error generating playbook: {str(e)}"


if __name__ == '__main__':
    # Example usage:
    sample_vulnerability = {
        'cve_id': 'CVE-2023-12345',
        'description': 'A critical remote code execution vulnerability exists in the imaginary web server application.',
        'cvss_v3_score': 9.8,
        'cvss_v3_severity': 'CRITICAL',
        'cpes': ['cpe:/a:vendor:imaginary_web_server:1.0']
    }
    recommendation = get_patch_recommendation(sample_vulnerability)
    print(f"Recommendation for CVE-2023-12345:\n{recommendation}")

    # Test caching
    print("\nFetching recommendation again (should be from cache)...")
    cached_recommendation = get_patch_recommendation(sample_vulnerability)
    print(cached_recommendation)

    # Example with playbook content
    sample_playbook = """
    - hosts: all
      tasks:
        - name: Update apt cache
          apt:
            update_cache: yes
          tags:
            - update_cache
    """
    print("\n--- Recommendation with Playbook Context ---")
    recommendation_with_context = get_patch_recommendation(sample_vulnerability, sample_playbook)
    print(recommendation_with_context) 