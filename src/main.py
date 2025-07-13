import json
import logging
import os
from vulnerability_analyzer import analyze_scan_data
from nvd_querier import fetch_cvss_scores
from ranking import rank_vulnerabilities
from patch_finder import find_patches_for_cves
from msrc_finder import find_msrc_patches

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_full_analysis(file_path: str) -> dict:
    """
    Runs the full vulnerability analysis pipeline.

    1. Reads and analyzes an Nmap XML file using an LLM.
    2. Extracts all identified CVEs.
    3. Fetches official CVSS scores from the NVD.
    4. Enriches the initial analysis with the fetched scores.

    Args:
        file_path: The path to the Nmap XML scan file.

    Returns:
        A dictionary containing the final, enriched vulnerability data,
        or an empty dictionary if the process fails.
    """
    logger.info(f"Starting analysis for file: {file_path}")

    # Step 1: Read the XML file
    try:
        with open(file_path, 'r') as f:
            xml_content = f.read()
    except FileNotFoundError:
        logger.error(f"Error: The file '{file_path}' was not found.")
        return {}

    # Step 2: Analyze scan data with the LLM to get initial findings
    logger.info("Calling vulnerability analyzer (LLM)...")
    initial_analysis = analyze_scan_data(xml_content)
    if not initial_analysis:
        logger.error("Vulnerability analysis failed or returned no data.")
        return {}
    logger.info("Initial analysis complete.")

    # Step 3: Collect all unique CVE IDs from the analysis
    cve_ids_to_fetch = set()
    for host_ip, host_data in initial_analysis.items():
        for service in host_data.get("services", []):
            for vuln in service.get("vulnerabilities", []):
                cve_id = vuln.get("cve_id")
                if cve_id and cve_id != "N/A":
                    cve_ids_to_fetch.add(cve_id)
    
    if not cve_ids_to_fetch:
        logger.warning("No CVEs found in the initial analysis. Returning as is.")
        return initial_analysis

    logger.info(f"Found {len(cve_ids_to_fetch)} unique CVEs to query.")

    # Step 4: Fetch CVSS scores from NVD
    logger.info("Fetching CVSS scores from NVD...")
    cvss_scores = fetch_cvss_scores(list(cve_ids_to_fetch))
    if not cvss_scores:
        logger.warning("Could not fetch any CVSS scores. Returning initial analysis.")
        return initial_analysis
    logger.info("CVSS score fetching complete.")

    # Step 5: Enrich the initial analysis with the new scores
    logger.info("Enriching analysis with CVSS scores...")
    enriched_analysis = initial_analysis.copy()
    for host_ip, host_data in enriched_analysis.items():
        for service in host_data.get("services", []):
            for vuln in service.get("vulnerabilities", []):
                cve_id = vuln.get("cve_id")
                if cve_id in cvss_scores and cvss_scores[cve_id]:
                    # Unpack the scores and assign them
                    scores = cvss_scores[cve_id]
                    vuln["cvss_score"] = scores.get("cvss_score")
                    vuln["exploitability_score"] = scores.get("exploitability_score")
    
    logger.info("Enrichment complete.")
    
    # Step 6: Rank the vulnerabilities based on their scores
    ranked_analysis = rank_vulnerabilities(enriched_analysis)
    
    # Step 7: Find patch information using a fallback strategy
    logger.info("Finding patch information for top vulnerabilities...")

    # Get the top 10 ranked CVEs to query
    all_vulns = sorted(
        [v for host in ranked_analysis.values() for s in host.get("services", []) for v in s.get("vulnerabilities", [])],
        key=lambda v: v.get('ranking', float('inf'))
    )
    top_cves = [v['cve_id'] for v in all_vulns[:10] if 'cve_id' in v and v['cve_id'] != "N/A"]

    if not top_cves:
        logger.info("No CVEs to fetch patch data for.")
        return ranked_analysis

    # Step 7.1: Query OSV.dev for all top CVEs first
    patch_data = find_patches_for_cves(top_cves)
    
    # Step 7.2: Identify CVEs that were not found in OSV.dev for MSRC fallback
    msrc_cves_to_fetch = []
    for cve_id, data in patch_data.items():
        if data.get("ecosystem") == "Not in OSV.dev":
            msrc_cves_to_fetch.append(cve_id)
            
    # Step 7.3: Query MSRC for the remaining CVEs and update the patch data
    if msrc_cves_to_fetch:
        msrc_patch_data = find_msrc_patches(msrc_cves_to_fetch)
        patch_data.update(msrc_patch_data)

    # Step 7.4: Enrich the final analysis with the consolidated patch data
    if patch_data:
        for host_data in ranked_analysis.values():
            for service in host_data.get("services", []):
                for vuln in service.get("vulnerabilities", []):
                    if vuln.get('cve_id') in patch_data:
                        vuln.update(patch_data[vuln['cve_id']])

    return ranked_analysis

if __name__ == '__main__':
    # The main entry point for running the orchestration script
    # Construct an absolute path to the Nmap file to ensure it's always found
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    NMAP_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'sample_nmap.xml')
    
    final_result = run_full_analysis(NMAP_FILE)

    if final_result:
        print("\n--- Final Enriched Analysis Result ---")
        print(json.dumps(final_result, indent=2))
        print("\n--------------------------------------")
    else:
        print("\nAnalysis pipeline failed to produce a result.")
