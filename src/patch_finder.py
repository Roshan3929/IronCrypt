import requests
import time
import logging
import os
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CORRECTED: Use the endpoint for direct vulnerability lookups ---
OSV_API_BASE_URL = "https://api.osv.dev/v1/vulns/"

def _get_patch_from_osv(cve_id: str, retries: int = 3, backoff_factor: float = 0.5) -> dict:
    """
    Queries the OSV.dev API for a single CVE ID with retry logic.

    Args:
        cve_id: The CVE ID to query.
        retries: The number of times to retry on failure.
        backoff_factor: A factor to determine the delay between retries.

    Returns:
        A dictionary with patch information or default "Unknown" values if not found or on error.
    """
    # --- CORRECTED: Construct the URL with the CVE ID ---
    url = f"{OSV_API_BASE_URL}{cve_id}"
    logger.info(f"Querying OSV.dev: {url}")

    for attempt in range(retries):
        try:
            # --- CORRECTED: Use a GET request, no JSON payload needed ---
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                # Successfully found vulnerability data
                data = response.json()
                
                # Default values if no patch info is found
                pkg_name = "Not specified"
                ecosystem = "Not specified"
                fixed_version = "Not specified"

                if 'affected' in data and data['affected']:
                    # Extract info from the first affected package entry
                    affected_package = data['affected'][0]
                    pkg_name = affected_package.get('package', {}).get('name', 'Not specified')
                    ecosystem = affected_package.get('package', {}).get('ecosystem', 'Not specified')

                    # Find the fixed version in the range events
                    for r in affected_package.get('ranges', []):
                        for e in r.get('events', []):
                            if 'fixed' in e:
                                fixed_version = e['fixed']
                                break
                        if fixed_version != "Not specified":
                            break
                
                return {
                    "package": pkg_name,
                    "ecosystem": ecosystem,
                    "fixed_version": fixed_version
                }
            elif response.status_code == 404:
                # 404 means the CVE is not in the OSV database, which is common for non-open-source software.
                logger.warning(f"OSV.dev has no information for {cve_id} (404 Not Found).")
                return {"package": "N/A", "ecosystem": "Not in OSV.dev", "fixed_version": "See vendor advisory"}
            
            # For other non-200 status codes, retry
            logger.warning(f"Request to OSV for {cve_id} failed with status {response.status_code}. Retrying...")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request to OSV for {cve_id} failed: {e}. Retrying...")

        # Exponential backoff
        time.sleep(backoff_factor * (2 ** attempt))
    
    # This is only reached if all retries fail for non-404 errors.
    logger.error(f"All retries failed for {cve_id}.")
    return {"package": "Error", "ecosystem": "API Request Failed", "fixed_version": "Check logs"}


def find_patches_for_cves(cve_ids: list[str]) -> dict:
    """
    Finds patch information for a list of CVE IDs by querying OSV.dev.

    Args:
        cve_ids: A list of CVE ID strings to look up.

    Returns:
        A dictionary mapping each CVE ID to its patch information.
    """
    logger.info(f"Querying OSV.dev for patch info for {len(cve_ids)} CVEs...")
    patch_info = {}
    for cve_id in cve_ids:
        patch_info[cve_id] = _get_patch_from_osv(cve_id)
    
    logger.info("OSV.dev patch lookup complete.")
    return patch_info

# Example usage
if __name__ == '__main__':
    # Test with a known CVE that has clear patch info in OSV
    sample_cves = ["CVE-2021-44228", "CVE-2024-3094", "CVE-BOGUS-9999"] 
    
    results = find_patches_for_cves(sample_cves)
    
    print("\n--- OSV.dev Patch Information ---")
    print(json.dumps(results, indent=2))
    print("---------------------------------")