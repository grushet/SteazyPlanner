import requests
import json
import random

# URL to a raw JSON file hosted on GitHub (Community maintained)
# This acts as your "Free API" endpoint
URL = "https://gist.githubusercontent.com/cmota/f7919cd962a061126effb2d7118bec72/raw/questions.json"

def get_sat_question():
    try:
        print("Fetching questions from GitHub...")
        response = requests.get(URL)
        
        if response.status_code == 200:
            data = response.json()
            
            # The structure of this specific JSON is a list of objects
            # Let's pick a random question to simulate an API
            question = random.choice(data)
            
            print("\n--- SAT QUESTION ---")
            print(f"Q: {question['question']}")
            print(f"A) {question['A']}")
            print(f"B) {question['B']}")
            print(f"C) {question['C']}")
            print(f"D) {question['D']}")
            print(f"Correct Answer: {question['answer']}")
            print("--------------------\n")
            
        else:
            print(f"Error: Unable to fetch data (Status code: {response.status_code})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_sat_question()