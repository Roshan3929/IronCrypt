import requests
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_API_KEY =  "f25d2382-7cc7-4afa-91ef-d14a9705eaef" # Optional: set your NVD API key here for better rate limits

# NVD rate limit (without API key): 5 requests per 30 seconds
RATE_LIMIT = 5
SLEEP_INTERVAL = 30


def fetch_cvss_scores(cve_ids):
    """
    Fetch CVSS and exploitability scores for a list of CVE IDs using the NVD API.
    Queries one CVE at a time to avoid request formatting issues.

    Args:
        cve_ids (list): List of CVE ID strings.

    Returns:
        dict: {cve_id: {'cvss_score': score, 'exploitability_score': exp_score}}
    """
    scores = {}
    headers = {"User-Agent": "VulnAnalyzer/1.0"}
    if NVD_API_KEY:
        headers["apiKey"] = NVD_API_KEY

    for index, cve_id in enumerate(cve_ids):
        # Initialize with a nested dictionary
        scores[cve_id] = {"cvss_score": None, "exploitability_score": None}
        params = {"cveId": cve_id}

        try:
            logger.info(f"Fetching data for {cve_id}...")
            response = requests.get(NVD_API_URL, headers=headers, params=params, timeout=10)

            if response.status_code == 404:
                logger.warning(f"CVE {cve_id} not found in NVD.")
            else:
                response.raise_for_status()
                data = response.json()

                vulnerabilities = data.get("vulnerabilities", [])
                if vulnerabilities:
                    cve_data = vulnerabilities[0].get("cve", {})
                    metrics = cve_data.get("metrics", {})

                    cvss_score = None
                    exploitability_score = None

                    if "cvssMetricV31" in metrics:
                        metric = metrics["cvssMetricV31"][0]
                        cvss_score = metric["cvssData"]["baseScore"]
                        exploitability_score = metric.get("exploitabilityScore")
                    elif "cvssMetricV30" in metrics:
                        metric = metrics["cvssMetricV30"][0]
                        cvss_score = metric["cvssData"]["baseScore"]
                        exploitability_score = metric.get("exploitabilityScore")
                    elif "cvssMetricV2" in metrics:
                        metric = metrics["cvssMetricV2"][0]
                        cvss_score = metric["cvssData"]["baseScore"]
                        exploitability_score = metric.get("exploitabilityScore")

                    scores[cve_id] = {
                        "cvss_score": cvss_score,
                        "exploitability_score": exploitability_score,
                    }

        except requests.exceptions.RequestException as e:
            logger.warning(f"Error fetching data for {cve_id} from NVD: {e}")
            # Scores for this CVE remain None.

        if not NVD_API_KEY:
            if (index + 1) % RATE_LIMIT == 0 and len(cve_ids) > (index + 1):
                logger.info(f"Made {RATE_LIMIT} requests. Sleeping for {SLEEP_INTERVAL} seconds...")
                time.sleep(SLEEP_INTERVAL)

    return scores