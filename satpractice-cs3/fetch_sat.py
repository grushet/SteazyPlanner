import requests
import json
import random


URL = "https://gist.githubusercontent.com/cmota/f7919cd962a061126effb2d7118bec72/raw/questions.json"

# Pinesat SAT‑questions API (math section)
PINESAT_URL = "https://pinesat.com/api/questions"


GEMINI_KEY = None  # or 'AIzaSyBBg5FZi5vUTJNmTC5C_JpDS5VOB9J-5s4'


def get_sat_question():
    """Demonstrates pulling one random question from the GitHub gist endpoint."""
    try:
        print("Fetching questions from GitHub...")
        response = requests.get(URL)
        
        if response.status_code == 200:
            data = response.json()
            question = random.choice(data)
            print("\n--- SAT QUESTION (gist) ---")
            print(f"Q: {question.get('question')}")
            for opt in ['A','B','C','D']:
                if opt in question:
                    print(f"{opt}) {question[opt]}")
            print(f"Correct Answer: {question.get('answer')}")
            print("--------------------\n")
        else:
            print(f"Error: Unable to fetch data (Status code: {response.status_code})")
    except Exception as e:
        print(f"Error: {e}")


def get_pinesat_questions(limit: int = 10):
    """Fetch a batch of 'limit' questions from Pinesat's public API."""
    try:
        print(f"Fetching {limit} questions from Pinesat API...")
        resp = requests.get(PINESAT_URL, params={"section": "math", "limit": limit})
        resp.raise_for_status()
        data = resp.json()
        print(f"Received {len(data)} items")
        return data
    except Exception as e:
        print(f"Error fetching Pinesat questions: {e}")
        return []


def generate_with_gemini(prompt: str):
    """Simple wrapper demonstrating a Gemini call using the predefined key."""
    if not GEMINI_KEY:
        print("Gemini key not set; skipping.")
        return None
    url = "https://gemini.googleapis.com/v1/models/text-bison-001:generate"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {GEMINI_KEY}"}
    payload = {"prompt": prompt, "temperature": 0.7, "max_output_tokens": 800}
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Gemini error: {e}")
        return None


if __name__ == "__main__":
    get_sat_question()
    # optionally demonstrate other sources
    p = get_pinesat_questions(5)
    print(p[:2])
    if GEMINI_KEY:
        print(generate_with_gemini("Give me 2 sample SAT math questions in JSON array format."))

if __name__ == "__main__":
    get_sat_question()