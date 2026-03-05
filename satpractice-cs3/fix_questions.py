import json

# Load the current questions.json
with open('data/questions.json', 'r') as f:
    data = json.load(f)

print("Loaded data")

# Convert the structure
new_data = {}
for topic, lessons in data.items():
    print(f"Topic: {topic}")
    new_data[topic] = {}
    for lesson_key, questions in lessons.items():
        print(f"Lesson key: {lesson_key}")
        # Change "lesson1" to "1"
        new_lesson_key = lesson_key.replace('lesson', '')
        print(f"New lesson key: {new_lesson_key}")
        new_questions = []
        for q in questions:
            new_q = q.copy()
            # make sure type field exists and normalize
            if new_q.get('type') == 'multiple-choice':
                new_q['type'] = 'mcq'
            if 'type' not in new_q:
                # assume multiple-choice by default
                new_q['type'] = 'mcq'
            # Convert choices from dict to list
            if isinstance(new_q.get('choices'), dict):
                new_q['choices'] = [new_q['choices'].get('A', ''), new_q['choices'].get('B', ''), new_q['choices'].get('C', ''), new_q['choices'].get('D', '')]
            # Convert answer from letter to index
            if isinstance(new_q.get('answer'), str):
                if new_q['answer'] in 'ABCD':
                    new_q['answer'] = 'ABCD'.index(new_q['answer'])
                else:
                    try:
                        new_q['answer'] = int(new_q['answer'])
                    except:
                        pass
with open('data/questions.json', 'w') as f:
    json.dump(new_data, f, indent=2)

print("Saved")