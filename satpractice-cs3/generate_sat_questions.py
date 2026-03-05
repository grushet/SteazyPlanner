#!/usr/bin/env python3
"""
SAT Question Generator using Claude AI
Generates realistic SAT practice questions for various topics
"""

import json
import os
import requests
import random

# Topics for SAT questions
TOPICS = {
    "arithmetic": "Basic arithmetic, percentages, ratios, fractions, and number properties",
    "geometry": "Angles, triangles, circles, area, perimeter, and coordinate geometry",
    "data-stats": "Data interpretation, statistics, probability, and graphs",
    "grammar": "Sentence structure, punctuation, grammar, and usage",
    "reading": "Reading comprehension, inference, and main ideas",
    "vocabulary": "Word meanings, context clues, and vocabulary usage"
}

def generate_questions(topic: str, num_questions: int = 4, num_lessons: int = 3, gemini_key: str | None = None) -> dict:
    """
    Generate SAT questions for a specific topic using Claude.
    
    Args:
        topic: The SAT topic (arithmetic, geometry, data-stats, grammar, reading, vocabulary)
        num_questions: Number of questions per lesson
        num_lessons: Number of lessons to generate
        
    Returns:
        Dictionary with topic data in the format for questions.json
    """
    
    if topic not in TOPICS:
        print(f"Invalid topic: {topic}")
        print(f"Valid topics: {', '.join(TOPICS.keys())}")
        return {}
    
    topic_description = TOPICS[topic]
    topic_data = {}
    conversation_history = []
    
    print(f"\n🎯 Generating SAT {topic.title()} Questions...")
    print(f"Topics: {topic_description}")
    print(f"Lessons: {num_lessons}, Questions per lesson: {num_questions}\n")
    
    for lesson_num in range(1, num_lessons + 1):
        print(f"📝 Generating Lesson {lesson_num}...")
        
        # Initial prompt for the lesson
        if lesson_num == 1:
            system_prompt = f"""You are an expert SAT test creator. You create realistic, challenging SAT questions.
            
For the topic '{topic}' ({topic_description}), generate {num_questions} SAT-style questions for Lesson {lesson_num}.

Format your response as a JSON array with exactly {num_questions} question objects. Each question should have:
- "id": unique identifier (e.g., "q1", "q2", etc.)
- "type": either "mcq" (multiple choice) or "short" (short answer)
- "question": the question text
- "choices": array of 4 options (for mcq type only)
- "answer": the correct answer (either index 0-3 for mcq, or the text answer for short)
- "explanation": detailed explanation of the answer

Make the questions progressively harder within the lesson. Use realistic SAT format.
Return ONLY the JSON array, no other text."""
        else:
            system_prompt = f"""You are an expert SAT test creator. Continue creating SAT questions for '{topic}'.
            
Generate {num_questions} NEW SAT-style questions for Lesson {lesson_num}. These should be different from previous lessons and cover different subtopics.

Format your response as a JSON array with exactly {num_questions} question objects. Each question should have:
- "id": unique identifier (e.g., "q1", "q2", etc.)
- "type": either "mcq" (multiple choice) or "short" (short answer)
- "question": the question text
- "choices": array of 4 options (for mcq type only)
- "answer": the correct answer (either index 0-3 for mcq, or the text answer for short)
- "explanation": detailed explanation of the answer

Make these questions slightly harder than previous lessons. Return ONLY the JSON array, no other text."""
        
        # Prepare message with context
        if lesson_num == 1:
            user_message = f"Generate lesson {lesson_num} SAT questions for {topic}."
        else:
            user_message = f"Generate lesson {lesson_num} SAT questions for {topic}. Make them different from previous lessons."
        
        # Prepare prompt for Gemini
        prompt = system_prompt + "\n\n" + user_message
        
        try:
            # Call Gemini API
            assistant_message = generate_with_gemini(prompt, gemini_key or "")
            
            # Parse the JSON response
            questions = json.loads(assistant_message)
            
            # Validate and format questions
            lesson_questions = []
            for i, q in enumerate(questions):
                # Ensure id format
                q["id"] = f"q{i+1}"
                
                # Validate MCQ questions
                if q.get("type") == "mcq":
                    if "choices" not in q or len(q["choices"]) != 4:
                        q["choices"] = ["Option A", "Option B", "Option C", "Option D"]
                    # Ensure answer is an index
                    if isinstance(q.get("answer"), str):
                        try:
                            q["answer"] = int(q["answer"])
                        except:
                            q["answer"] = 0
                
                lesson_questions.append(q)
            
            topic_data[str(lesson_num)] = lesson_questions
            print(f"✅ Lesson {lesson_num} generated with {len(lesson_questions)} questions")
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON for lesson {lesson_num}: {e}")
            # Create placeholder questions if parsing fails
            topic_data[str(lesson_num)] = [
                {
                    "id": "q1",
                    "type": "mcq",
                    "question": f"Sample question for {topic} lesson {lesson_num}",
                    "choices": ["A", "B", "C", "D"],
                    "answer": 0,
                    "explanation": "This is a placeholder question."
                }
            ]
        except Exception as e:
            print(f"❌ Error generating lesson {lesson_num}: {e}")
    
    # Optionally make sure each lesson has at least the requested number of questions
    # (in case external sources were used to fill gaps)
    return topic_data


def generate_all_topics(num_questions: int = 4, num_lessons: int = 3, gemini_key: str | None = None) -> dict:
    """Generate questions for all SAT topics."""
    all_data = {}
    
    for topic in TOPICS.keys():
        all_data[topic] = generate_questions(topic, num_questions, num_lessons, gemini_key)
    
    return all_data



# --- external sources helpers ------------------------------------------------

def fetch_pinesat_questions(limit: int = 10, section: str = "math") -> list:
    """Retrieve a batch of questions from the public Pinesat API.

    The endpoint returns a JSON list; the schema varies so we perform a best-effort
    normalization later.
    """
    try:
        resp = requests.get("https://pinesat.com/api/questions",
                            params={"section": section, "limit": limit},
                            timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"⚠️  Could not fetch from Pinesat: {e}")
        return []


def generate_with_gemini(prompt: str, api_key: str) -> str:
    """Call the Google Gemini API and return raw text."""
    if not api_key:
        fallback = [{"id": f"q{i+1}", "type": "mcq", "question": f"Sample question {i+1}", "choices": ["A", "B", "C", "D"], "answer": 0, "explanation": "Sample"} for i in range(20)]
        return json.dumps(fallback)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500}
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        out = r.json()
        # Extract text from Gemini response
        if "candidates" in out and out["candidates"]:
            content = out["candidates"][0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "")
        fallback = [{"id": f"q{i+1}", "type": "mcq", "question": f"Sample question {i+1}", "choices": ["A", "B", "C", "D"], "answer": 0, "explanation": "Sample"} for i in range(20)]
        return json.dumps(fallback)
    except Exception as e:
        print(f"⚠️  Gemini API error: {e}")
        fallback = [{"id": f"q{i+1}", "type": "mcq", "question": f"Sample question {i+1}", "choices": ["A", "B", "C", "D"], "answer": 0, "explanation": "Sample"} for i in range(20)]
        return json.dumps(fallback)


def normalize_external_question(raw: object, fallback_id: str) -> dict:
    """Convert a raw object from an external service into our internal format."""
    q = {"id": fallback_id, "type": "short", "question": "", "answer": "", "explanation": ""}
    if isinstance(raw, dict):
        question_data = raw.get("question", {})
        if isinstance(question_data, dict):
            q["question"] = question_data.get("question", "")
            choices = question_data.get("choices", {})
            ans = question_data.get("correct_answer", "")
            explanation = question_data.get("explanation", "")
        else:
            q["question"] = question_data or raw.get("text", "") or str(raw)
            choices = raw.get("choices", {}) or raw.get("options", [])
            ans = raw.get("answer") or raw.get("correct", "")
            explanation = raw.get("explanation", "")
        
        if choices:
            q["type"] = "mcq"
            if isinstance(choices, dict):
                q["choices"] = [choices.get(k, "") for k in ["A", "B", "C", "D"]]
            else:
                q["choices"] = choices
        
        if isinstance(ans, str):
            if ans.isdigit():
                q["answer"] = int(ans)
            else:
                letters = "ABCD"
                if ans.upper() in letters:
                    q["answer"] = letters.index(ans.upper())
                else:
                    q["answer"] = 0
        else:
            q["answer"] = ans
        
        q["explanation"] = explanation
    else:
        q["question"] = str(raw)
    return q


def ensure_minimum(data: dict,
                   min_lessons: int = 10,
                   min_questions: int = 20,
                   gemini_key: str | None = None,
                   include_pinesat: bool = False) -> dict:
    """Make sure every topic contains at least *min_lessons* lessons and
    each lesson has at least *min_questions* questions.

    External sources are used to fill holes when requested.
    """
    # build a pool of pinesat items if needed
    pinesat_pool = []
    if include_pinesat:
        pinesat_pool = fetch_pinesat_questions(limit=min_lessons * min_questions * len(TOPICS))
        random.shuffle(pinesat_pool)

    for topic in TOPICS.keys():
        lessons = data.setdefault(topic, {})
        for lnum in range(1, min_lessons + 1):
            key = str(lnum)
            lesson_qs = lessons.setdefault(key, [])

            # if gemini key and lesson completely empty, try to generate a batch
            if gemini_key and not lesson_qs:
                prompt = (f"Create {min_questions} SAT-style {topic} questions for lesson {lnum}. "
                          "Return an array of JSON objects with fields id,type,question,choices,answer,explanation.")
                text = generate_with_gemini(prompt, gemini_key)
                try:
                    extra = json.loads(text)
                    if isinstance(extra, list):
                        for q in extra:
                            lesson_qs.append(q)
                except:
                    # ignore parse errors
                    pass

            # fill remaining slots from pinesat pool or by cloning existing questions
            while len(lesson_qs) < min_questions:
                if pinesat_pool:
                    raw = pinesat_pool.pop(0)
                    lesson_qs.append(normalize_external_question(raw, f"{topic}{lnum}q{len(lesson_qs)+1}"))
                elif lesson_qs:
                    base = random.choice(lesson_qs)
                    new = base.copy()
                    new["id"] = f"{topic}{lnum}q{len(lesson_qs)+1}"
                    lesson_qs.append(new)
                else:
                    lesson_qs.append({"id": f"{topic}{lnum}q{len(lesson_qs)+1}",
                                      "type": "short",
                                      "question": "Placeholder question",
                                      "answer": "",
                                      "explanation": ""})

    return data


def save_questions(data: dict, filename: str = "questions.json"):
    """Save generated questions to a JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), "data", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Questions saved to {filepath}")


def main():
    """Main function to generate SAT questions."""
    with open(os.path.join(os.path.dirname(__file__), 'debug.txt'), 'w') as f:
        f.write('main started\n')
    
    print("🎓 SAT Question Generator with Claude AI")
    print("=" * 50)
    
    # Ask user for options
    print("\nOptions:")
    print("1. Generate questions for a specific topic")
    print("2. Generate questions for all topics")
    print("3. Interactive mode (generate and refine)")
    print("4. Regenerate/augment using external sources (Pinesat + Gemini – ensures 10 lessons×20 questions)")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        print("\nAvailable topics:")
        for i, topic in enumerate(TOPICS.keys(), 1):
            print(f"{i}. {topic}")
        
        topic_choice = input("\nSelect topic (1-6 or name): ").strip()
        
        # Map choice to topic
        if topic_choice.isdigit():
            topics = list(TOPICS.keys())
            if 1 <= int(topic_choice) <= len(topics):
                topic = topics[int(topic_choice) - 1]
            else:
                print("Invalid choice")
                return
        else:
            topic = topic_choice.lower()
        
        if topic not in TOPICS:
            print(f"Invalid topic: {topic}")
            return
        
        num_lessons = int(input("Number of lessons (default 3): ") or "3")
        num_questions = int(input("Questions per lesson (default 4): ") or "4")
        gemini_key = input("Google Gemini API key (optional): ").strip() or None
        
        questions = generate_questions(topic, num_questions, num_lessons, gemini_key)
        
        # Save this topic or merge with existing
        existing_file = os.path.join(os.path.dirname(__file__), "data", "questions.json")
        if os.path.exists(existing_file):
            with open(existing_file, 'r') as f:
                all_data = json.load(f)
            all_data[topic] = questions
        else:
            all_data = {topic: questions}
        
        save_questions(all_data)
        
    elif choice == "2":
        num_lessons = int(input("Number of lessons per topic (default 3): ") or "3")
        num_questions = int(input("Questions per lesson (default 4): ") or "4")
        gemini_key = input("Google Gemini API key (optional): ").strip() or None
        
        all_questions = generate_all_topics(num_questions, num_lessons, gemini_key)
        save_questions(all_questions)
        
    elif choice == "3":
        print("\n🤖 Interactive Mode - Generate and Refine Questions")
        topic = input("Enter topic (arithmetic/geometry/data-stats/grammar/reading/vocabulary): ").strip().lower()
    elif choice == "4":
        # Use external APIs to build a large question bank with minimum structure
        gemini_key = input("Google Gemini API key (press enter to skip): ").strip() or None
        include_pinesat = input("Include Pinesat questions? (y/n): ").strip().lower().startswith('y')
        print("Generating base dataset with Claude, then augmenting...")
        all_questions = generate_all_topics(num_questions=0, num_lessons=10)
        all_questions = ensure_minimum(all_questions,
                                       min_lessons=10,
                                       min_questions=20,
                                       gemini_key=gemini_key,
                                       include_pinesat=include_pinesat)
        save_questions(all_questions)


if __name__ == "__main__":
    main()
    with open(os.path.join(os.path.dirname(__file__), 'debug.txt'), 'a') as f:
        f.write('script done\n')








#hejgf gnfkf aksfnkfoj dd