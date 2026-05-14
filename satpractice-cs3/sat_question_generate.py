"""
generate_sat_questions.py

Pulls real SAT-style questions from two free sources and saves to data/questions.json.
No API key needed. No cost.

Sources:
  - PineSAT API (https://pinesat.com/api/questions)
      Reading, Grammar, Vocabulary questions
  - MAmmoTH GitHub dataset
      Math questions (Arithmetic, Algebra, Geometry, Data & Stats)

Requirements:
    pip install requests

Usage:
    python generate_sat_questions.py
"""

import requests
import json
import os
import random
import re
import sys

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "questions.json")

PINESAT_URL   = "https://pinesat.com/api/questions"
MAMMOTH_URL   = "https://raw.githubusercontent.com/TIGER-AI-Lab/MAmmoTH/main/math_eval/dataset/sat/sat.json"

LESSONS_PER_TOPIC = 10
QUESTIONS_PER_LESSON = 10


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def fetch_json(url, params=None, label=""):
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  ERROR fetching {label}: {e}")
        return None


def letter_to_index(letter):
    """Convert 'A'/'B'/'C'/'D' to 0/1/2/3."""
    mapping = {"A": 0, "B": 1, "C": 2, "D": 3}
    return mapping.get(str(letter).strip().upper(), 0)


def difficulty_label(lesson_num):
    if lesson_num <= 3:   return "Easy"
    elif lesson_num <= 7: return "Medium"
    else:                 return "Hard"


def assign_to_lessons(questions, n_lessons=10, per_lesson=10):
    """
    Sort questions by difficulty (Easy -> Medium -> Hard), then
    distribute across n_lessons in order.
    """
    order = {"Easy": 0, "Medium": 1, "Hard": 2}
    questions.sort(key=lambda q: order.get(q.get("difficulty", "Medium"), 1))

    lessons = {}
    for lesson_num in range(1, n_lessons + 1):
        want_diff = difficulty_label(lesson_num)
        diff_pool = [q for q in questions if q.get("difficulty") == want_diff]
        random.shuffle(diff_pool)

        if len(diff_pool) < per_lesson:
            # Top up from adjacent difficulties
            all_pool = [q for q in questions]
            random.shuffle(all_pool)
            diff_pool = diff_pool + [q for q in all_pool if q not in diff_pool]

        lessons[str(lesson_num)] = diff_pool[:per_lesson]

    return lessons



# PINESAT 

def fetch_pinesat(limit=500):
    print(f"Fetching {limit} questions from PineSAT API...")
    data = fetch_json(PINESAT_URL, params={"limit": limit}, label="PineSAT")
    if not data or not isinstance(data, list):
        print("  PineSAT returned no data.")
        return []

    print(f"  Got {len(data)} raw questions.")
    converted = []
    for item in data:
        try:
            q = item.get("question", {})
            choices_raw = q.get("choices", {})

            # choices is a dict {"A": "...", "B": "...", "C": "...", "D": "..."}
            if isinstance(choices_raw, dict):
                choices = [
                    choices_raw.get("A", ""),
                    choices_raw.get("B", ""),
                    choices_raw.get("C", ""),
                    choices_raw.get("D", ""),
                ]
            else:
                continue

            question_text = q.get("question", "").strip()
            paragraph     = q.get("paragraph", "null").strip()
            explanation   = q.get("explanation", "").strip()
            correct_letter = q.get("correct_answer", "A")
            answer_index  = letter_to_index(correct_letter)
            difficulty    = item.get("difficulty", "Medium")
            domain        = item.get("domain", "")

            if not question_text or not all(choices):
                continue

            entry = {
                "question":    question_text,
                "choices":     choices,
                "answer":      answer_index,
                "explanation": explanation,
                "difficulty":  difficulty,
                "type":        "mcq",
                "domain":      domain,
            }

            # If there's a real paragraph/passage, attach it
            if paragraph and paragraph.lower() != "null" and len(paragraph) > 40:
                entry["passage"] = paragraph

            converted.append(entry)
        except Exception:
            continue

    print(f"  Converted {len(converted)} usable questions.")
    return converted



# MAMMOTH — fetch SAT math questions and convert format


def fetch_mammoth():
    print("Fetching SAT math questions from MAmmoTH dataset...")
    data = fetch_json(MAMMOTH_URL, label="MAmmoTH")
    if not data or not isinstance(data, list):
        print("  MAmmoTH returned no data.")
        return []

    print(f"  Got {len(data)} raw math questions.")
    converted = []

    for item in data:
        try:
            raw_q = item.get("question", "")
            # Format: "Question text \nAnswer Choices: (A) ... (B) ... (C) ... (D) ..."
            if "Answer Choices:" in raw_q:
                parts = raw_q.split("Answer Choices:")
                question_text = parts[0].strip()
                choices_text  = parts[1].strip()
            else:
                question_text = raw_q.strip()
                choices_text  = ""

            # Parse choices like "(A) text (B) text (C) text (D) text"
            choice_matches = re.findall(r'\([A-D]\)\s*([^(]+?)(?=\s*\([A-D]\)|$)', choices_text)
            choices = [c.strip() for c in choice_matches]

            if len(choices) != 4:
                continue

            correct_letter = item.get("answer", "A")
            # answer might be just "A" or might be "(A)" or "A) text"
            clean_letter = re.sub(r'[^A-D]', '', str(correct_letter).upper())
            if not clean_letter:
                continue
            answer_index = letter_to_index(clean_letter[0])

            # Clean up LaTeX a bit for display
            q_clean = question_text.replace("$$", "").replace("\\\\", "\n")
            q_clean = re.sub(r'\$([^$]+)\$', r'\1', q_clean).strip()

            converted.append({
                "question":    q_clean,
                "choices":     choices,
                "answer":      answer_index,
                "explanation": item.get("answer", ""),
                "difficulty":  "Medium",
                "type":        "mcq",
                "domain":      "Math",
            })
        except Exception:
            continue

    print(f"  Converted {len(converted)} usable math questions.")
    return converted


# -----------------------------------------------------------------------
# DOMAIN → TOPIC MAPPING
# -----------------------------------------------------------------------

READING_DOMAINS = {"Information and Ideas", "Craft and Structure"}
GRAMMAR_DOMAINS = {"Standard English Conventions", "Expression of Ideas"}

def categorize_english(questions):
    """Split English questions into reading, grammar, and vocabulary buckets."""
    reading  = []
    grammar  = []
    vocab    = []

    for q in questions:
        domain = q.get("domain", "")
        text   = q.get("question", "").lower()

        # Vocabulary: word-meaning questions
        if ("most nearly means" in text or
            "as used" in text or
            "best defines" in text or
            "meaning of the word" in text):
            vocab.append(q)
        elif domain in READING_DOMAINS:
            reading.append(q)
        elif domain in GRAMMAR_DOMAINS:
            grammar.append(q)
        else:
            grammar.append(q)

    return reading, grammar, vocab


def categorize_math(questions):
    """
    Split math questions into arithmetic, algebra, geometry, data-stats.
    Since MAmmoTH doesn't tag by sub-topic, distribute roughly evenly
    while using keyword hints.
    """
    arithmetic = []
    algebra    = []
    geometry   = []
    data_stats = []

    geo_keywords   = ["angle", "triangle", "circle", "area", "perimeter",
                      "radius", "diameter", "volume", "coordinate", "slope",
                      "hypotenuse", "degree", "polygon", "rectangle", "square",
                      "sector", "arc", "tangent", "sine", "cosine"]
    data_keywords  = ["mean", "median", "average", "probability", "percent",
                      "data", "table", "survey", "distribution", "standard deviation",
                      "graph", "chart", "population", "sample"]
    algebra_keywords = ["equation", "inequality", "function", "variable",
                        "solve for", "linear", "quadratic", "polynomial",
                        "system", "factor", "expression", "f(x)", "slope",
                        "intercept"]

    for q in questions:
        text = (q.get("question", "") + " ".join(q.get("choices", []))).lower()
        if any(k in text for k in geo_keywords):
            geometry.append(q)
        elif any(k in text for k in data_keywords):
            data_stats.append(q)
        elif any(k in text for k in algebra_keywords):
            algebra.append(q)
        else:
            arithmetic.append(q)

    return arithmetic, algebra, geometry, data_stats


# MAIN


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)
        print("Deleted old questions.json. Starting fresh.\n")

    # Fetch all source data
    english_raw = fetch_pinesat(limit=500)
    math_raw    = fetch_mammoth()

    if not english_raw and not math_raw:
        print("Could not fetch any questions. Check your internet connection.")
        sys.exit(1)

    # Categorize
    reading_pool, grammar_pool, vocab_pool = categorize_english(english_raw)
    arith_pool, algebra_pool, geo_pool, stats_pool = categorize_math(math_raw)

    need = LESSONS_PER_TOPIC * QUESTIONS_PER_LESSON
    print(f"\nQuestion pool sizes:")
    print(f"  reading:     {len(reading_pool)}  (need {need})")
    print(f"  grammar:     {len(grammar_pool)}  (need {need})")
    print(f"  vocabulary:  {len(vocab_pool)}  (need {need})")
    print(f"  arithmetic:  {len(arith_pool)}  (need {need})")
    print(f"  algebra:     {len(algebra_pool)}  (need {need})")
    print(f"  geometry:    {len(geo_pool)}  (need {need})")
    print(f"  data-stats:  {len(stats_pool)}  (need {need})")

    # Pad any small pools by cycling
    def pad(pool, target):
        if len(pool) == 0:
            return []
        while len(pool) < target:
            pool = pool + pool
        return pool[:target]

    data = {
        "reading":    assign_to_lessons(pad(reading_pool,  need)),
        "grammar":    assign_to_lessons(pad(grammar_pool,  need)),
        "vocabulary": assign_to_lessons(pad(vocab_pool,    need)),
        "arithmetic": assign_to_lessons(pad(arith_pool,    need)),
        "algebra":    assign_to_lessons(pad(algebra_pool,  need)),
        "geometry":   assign_to_lessons(pad(geo_pool,      need)),
        "data-stats": assign_to_lessons(pad(stats_pool,    need)),
    }

    # For reading: attach the passage to the first question in each lesson
    # (passages are already on individual questions from PineSAT)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {OUTPUT_PATH}")
    print("\nSummary:")
    for topic, lessons in data.items():
        total = sum(len(v) for v in lessons.values())
        print(f"  {topic}: {len(lessons)} lessons, {total} questions")

    print("\nDone.")


if __name__ == "__main__":
    main()