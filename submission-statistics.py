import requests
import pandas as pd
import time
import concurrent.futures
import logging
import os

# Configure logging
logging.basicConfig(
    filename='error_submission.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# API request headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Accept": "text/html",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip",
    "Referer": "https://google.com/",
}

CSV_FILENAME = "problem_submissions.csv"

def get_contest():
    """Fetches the list of Codeforces contests."""
    url = "https://codeforces.com/api/contest.list"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        results = response.json()
        return results["result"]
    except requests.RequestException as e:
        logging.error(f"Failed to fetch contests: {e}")
        print(f"[error] Failed to fetch contests: {e}")
        return []

def get_submissions_count(contest_id):
    """Fetches submissions for a contest and returns formatted data."""
    url = f"https://codeforces.com/api/contest.status?contestId={contest_id}"
    accepted_count = {}
    total_count = {}
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        logging.error(f"Failed to fetch submissions for contest {contest_id}. Status code: {response.status_code}")
        print(f"[error] Failed to fetch submissions for contest {contest_id}. Status code: {response.status_code}")
        return accepted_count, total_count
    results = response.json()
    print("[info] Fetched submissions for contest", contest_id)
    for submission in results["result"]:
        accepted_count[(submission["problem"]["contestId"], submission["problem"]["index"])] = accepted_count.get((submission["problem"]["contestId"], submission["problem"]["index"]), 0) + (submission["verdict"] == "OK")
        total_count[(submission["problem"]["contestId"], submission["problem"]["index"])] = total_count.get((submission["problem"]["contestId"], submission["problem"]["index"]), 0) + 1
    return accepted_count, total_count

def get_errored_contest_ids():
    """Fetches the list of contest ids for which submissions fetching failed."""
    if not os.path.exists("error_submission.log"):
        return []
    res = []
    with open("error_submission.log", "r") as file:
        lines = file.readlines()
        for line in lines :
            res.append({"id":line.split(". ")[0].split(" ")[-1].strip(), "phase":"FINISHED"})
        return res
    

if __name__ == "__main__":
    contests = get_contest()
    current_process = contests
    i = True
    j = 0
    if contests:
        for current in current_process:
            if current["phase"] != "FINISHED":
                continue
            print(f"Processed contest {j + 1} of {len(current_process)}")
            accepted_count, total_count = get_submissions_count(current["id"])
            print("[success] submission counts are successfully fetched for ", current["id"])
            ## put the acceptance rate accepted_count total_count of a problem in a csv
            df = pd.DataFrame(list(accepted_count.items()), columns=["problem", "accepted_count"])
            df["total_count"] = df["problem"].map(total_count)
            if i == False:
                df.to_csv(CSV_FILENAME, index=False)
                i = True

            else:
                df.to_csv(CSV_FILENAME, mode='a', header=not os.path.exists(CSV_FILENAME), index=False)

            print("[info] Waiting for 5 seconds before fetching next contest submissions.")
            j += 1
            time.sleep(5)


    else:
        print("[error] No contests available.")