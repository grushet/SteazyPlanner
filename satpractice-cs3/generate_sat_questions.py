#!/usr/bin/env python3
"""
SAT Question Generator using Claude AI
Generates realistic SAT practice questions for various topics
"""

import json
import os
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic()

# Topics for SAT questions
TOPICS = {
    "arithmetic": "Basic arithmetic, percentages, ratios, fractions, and number properties",
    "geometry": "Angles, triangles, circles, area, perimeter, and coordinate geometry",
    "data-stats": "Data interpretation, statistics, probability, and graphs",
    "grammar": "Sentence structure, punctuation, grammar, and usage",
    "reading": "Reading comprehension, inference, and main ideas",
    "vocabulary": "Word meanings, context clues, and vocabulary usage"
}

def generate_questions(topic: str, num_questions: int = 4, num_lessons: int = 3) -> dict:
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
        
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Call Claude API with conversation history
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=system_prompt,
                messages=conversation_history
            )
            
            assistant_message = response.content[0].text
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
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
    
    return topic_data


def generate_all_topics(num_questions: int = 4, num_lessons: int = 3) -> dict:
    """Generate questions for all SAT topics."""
    all_data = {}
    
    for topic in TOPICS.keys():
        all_data[topic] = generate_questions(topic, num_questions, num_lessons)
    
    return all_data


def save_questions(data: dict, filename: str = "questions.json"):
    """Save generated questions to a JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), "data", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Questions saved to {filepath}")


def main():
    """Main function to generate SAT questions."""
    print("🎓 SAT Question Generator with Claude AI")
    print("=" * 50)
    
    # Ask user for options
    print("\nOptions:")
    print("1. Generate questions for a specific topic")
    print("2. Generate questions for all topics")
    print("3. Interactive mode (generate and refine)")
    
    choice = input("\nSelect option (1-3): ").strip()
    
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
        
        questions = generate_questions(topic, num_questions, num_lessons)
        
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
        
        all_questions = generate_all_topics(num_questions, num_lessons)
        save_questions(all_questions)
        
    elif choice == "3":
        print("\n🤖 Interactive Mode - Generate and Refine Questions")
        topic = input("Enter topic (arithmetic/geometry/data-stats/grammar/reading/vocabulary): ").strip().lower()
        
        if topic not in TOPICS:
            print("Invalid topic")
            return
        
        conversation = []
        lesson_num = 1
        all_lessons = {}
        
        while True:
            print(f"\n📚 Lesson {lesson_num}")
            
            if lesson_num == 1:
                prompt = f"Generate 4 SAT {topic} questions for lesson {lesson_num}"
            else:
                prompt = input("What would you like (generate/refine/next/save/quit)? ").strip().lower()
                
                if prompt == "quit":
                    break
                elif prompt == "save":
                    all_questions = {topic: all_lessons}
                    save_questions(all_questions)
                    print("✅ Questions saved!")
                    break
                elif prompt == "next":
                    lesson_num += 1
                    continue
            
            conversation.append({"role": "user", "content": prompt})
            
            try:
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=conversation
                )
                
                assistant_response = response.content[0].text
                conversation.append({"role": "assistant", "content": assistant_response})
                
                print(f"\n{assistant_response}")
                
                # Try to parse if it's JSON
                try:
                    questions = json.loads(assistant_response)
                    all_lessons[str(lesson_num)] = questions
                except:
                    pass
                    
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()








#hejgf gnfkf aksfnkfoj dd