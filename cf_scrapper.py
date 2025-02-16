import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("error.log"),
        logging.StreamHandler()
    ]
)

def get_problem_statement(problem_link):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Accept": "text/html",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip",
            "Referer": "https://www.google.com/",
        }
        response = requests.get(problem_link, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch the problem page. Status code: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        problem_statement = get_statement(soup) + "\n\n" + get_input_specification(soup) + "\n\n" + get_output_specification(soup)

        return problem_statement
    except Exception as e:
        print(f"[error] Error fetching problem statement for {problem_link}: {e}")
        logging.error(f"Error fetching problem statement for {problem_link}: {e}")
        return None

def get_statement(soup):
    statement_div = soup.find("div", {"class": "problem-statement"})
    if statement_div:
        child_divs = statement_div.find_all("div", recursive=False)
        if len(child_divs) > 1:
            return child_divs[1].text.strip()
    return ""

def get_input_specification(soup):
    input_spec_div = soup.find("div", {"class": "input-specification"})
    if input_spec_div:
        section_title_div = input_spec_div.find("div", {"class": "section-title"})
        if section_title_div:
            section_title_div.decompose()
        return input_spec_div.text.strip()
    return ""

def get_output_specification(soup):
    output_spec_div = soup.find("div", {"class": "output-specification"})
    if output_spec_div:
        section_title_div = output_spec_div.find("div", {"class": "section-title"})
        if section_title_div:
            section_title_div.decompose()
        return output_spec_div.text.strip()
    return ""

def list_problems():
    try:
        url = "https://codeforces.com/api/problemset.problems"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch the problem list. Status code: {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"[error] Error fetching problem list: {e}")
        logging.error(f"Error fetching problem list: {e}")
        return None

if __name__ == "__main__":
    problems = list_problems()
    ## cluster wise
    problems_ = problems['result']['problems'][0:15]
    
    if problems and 'result' in problems:
        ## replace problems['result']['problems'] with problems_ to fetch like cluster wise
        for problem in problems_ :
            try:
                contest_id = problem.get('contestId', None)
                problem_index = problem.get('index', None)
                problem_name = problem.get('name', None)
                problem_rating = problem.get('rating', None)
                problem_tags = problem.get('tags', None)
                problem_link = f"https://codeforces.com/problemset/problem/{contest_id}/{problem_index}"

                print(f"[info] Fetching problem: {problem_name} ({problem_link})")
                problem_statement = get_problem_statement(problem_link)
                
                if problem_statement:
                    df = pd.DataFrame(columns=['contest_id', 'problem_index', 'problem_name', 'problem_rating', 'problem_tags', 'problem_statement'], 
                                      data=[[contest_id, problem_index, problem_name, problem_rating, problem_tags, problem_statement]])
                    df.to_csv('problems.csv', mode='a', header=False, index=False)

                    print(f"[success] Problem {problem_name} fetched successfully")
                time.sleep(5)
            except Exception as e:
                print(f"[error] Error processing problem {problem_name}: {e}")
                logging.error(f"Error processing problem {problem_name}: {e}")
                continue