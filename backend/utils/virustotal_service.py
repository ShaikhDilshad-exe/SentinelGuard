import hashlib
import requests

# ---------------------------------------------------------
# VIRUSTOTAL CONFIG
# ---------------------------------------------------------
API_KEY = "da908589488aabd5369a63df46132f909c4c43fc96ed55be4b79c50f1d636231"

BASE_URL = "https://www.virustotal.com/api/v3/files"


# ---------------------------------------------------------
# CALCULATE SHA256
# ---------------------------------------------------------
def calculate_sha256(file_bytes):

    sha256 = hashlib.sha256()

    sha256.update(file_bytes)

    return sha256.hexdigest()


# ---------------------------------------------------------
# CHECK FILE HASH
# ---------------------------------------------------------
def check_file_hash(file_hash):

    headers = {
        "x-apikey": API_KEY
    }

    try:

        response = requests.get(
            f"{BASE_URL}/{file_hash}",
            headers=headers
        )

        # File found
        if response.status_code == 200:

            data = response.json()

            stats = data["data"]["attributes"][
                "last_analysis_stats"
            ]

            return {
                "found": True,
                "malicious": stats.get(
                    "malicious",
                    0
                ),
                "suspicious": stats.get(
                    "suspicious",
                    0
                ),
                "stats": stats
            }

        # File not found
        return {
            "found": False
        }

    except Exception as e:

        print(
            f"VirusTotal Error: {e}"
        )

        return {
            "found": False,
            "error": str(e)
        }