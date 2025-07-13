import logging

# Set up logging
logger = logging.getLogger(__name__)

def rank_vulnerabilities(analysis_data: dict) -> dict:
    """
    Ranks vulnerabilities in the analysis data based on a prioritization score.

    The prioritization score is calculated as: cvss_score * exploitability_score.
    A new 'ranking' field is added to each vulnerability.

    Args:
        analysis_data: The enriched vulnerability data from the main pipeline.

    Returns:
        The analysis data with an added 'ranking' for each vulnerability.
    """
    logger.info("Starting vulnerability ranking...")

    # Step 1: Flatten the list of vulnerabilities to make sorting easier.
    # We keep a reference to the original vulnerability object to modify it in place.
    vulnerabilities_to_rank = []
    for host_ip, host_data in analysis_data.items():
        for service in host_data.get("services", []):
            for vuln in service.get("vulnerabilities", []):
                vulnerabilities_to_rank.append(vuln)

    if not vulnerabilities_to_rank:
        logger.warning("No vulnerabilities found to rank.")
        return analysis_data

    # Step 2: Calculate a prioritization score for each vulnerability.
    # We use a lambda that defaults to 0 if scores are None or missing.
    get_score = lambda v: (v.get('cvss_score') or 0) * (v.get('exploitability_score') or 0)

    # Step 3: Sort the list of vulnerabilities in descending order of their score.
    vulnerabilities_to_rank.sort(key=get_score, reverse=True)

    # Step 4: Assign a rank to each vulnerability object based on its sorted position.
    for i, vuln in enumerate(vulnerabilities_to_rank):
        vuln['ranking'] = i + 1
        
    logger.info("Vulnerability ranking complete.")
    
    # The original analysis_data dictionary has been modified in place.
    # We return it for clarity and good practice.
    return analysis_data
