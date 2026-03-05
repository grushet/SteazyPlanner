import json
import random
from fractions import Fraction

# Load Pinesat questions
with open('pinesat_sample.json', 'r') as f:
    pinesat_data = json.load(f)

pinesat_questions = []
for item in pinesat_data:
    if item['domain'] in ['Algebra', 'Advanced Math', 'Problem-Solving and Data Analysis'] and item['difficulty'] in ['Easy', 'Medium', 'Hard']:
        q = item['question']
        pinesat_questions.append({
            'question': q['question'],
            'choices': q['choices'],
            'answer': q['correct_answer'],
            'explanation': q['explanation'],
            'difficulty': item['difficulty']
        })

def generate_basic_operations():
    a = random.randint(10, 50)
    b = random.randint(10, 50)
    op = random.choice(['+', '-', '*'])
    if op == '-':
        a, b = max(a,b), min(a,b)
    question = f"What is {a} {op} {b}?"
    if op == '+':
        correct = a + b
    elif op == '-':
        correct = a - b
    else:
        correct = a * b
    choices = [correct, correct + random.randint(1,10), correct - random.randint(1,10), correct + random.randint(-5,5)]
    random.shuffle(choices)
    answer = chr(65 + choices.index(correct))
    explanation = f"{a} {op} {b} = {correct}"
    return {
        "question": question,
        "choices": {chr(65+i): str(choices[i]) for i in range(4)},
        "answer": answer,
        "explanation": explanation,
        "difficulty": "Easy"
    }

def generate_fractions():
    a = random.randint(1,10)
    b = random.randint(2,10)
    c = random.randint(1,10)
    d = random.randint(2,10)
    f1 = Fraction(a, b)
    f2 = Fraction(c, d)
    op = random.choice(['+', '-'])
    if op == '-':
        f1, f2 = max(f1, f2), min(f1, f2)
    question = f"What is {a}/{b} {op} {c}/{d}?"
    if op == '+':
        correct = f1 + f2
    else:
        correct = f1 - f2
    choices = [correct, correct + Fraction(1, random.randint(2,5)), correct - Fraction(1, random.randint(2,5)), correct + Fraction(random.randint(-2,2), random.randint(2,5))]
    random.shuffle(choices)
    answer = chr(65 + choices.index(correct))
    explanation = f"{a}/{b} {op} {c}/{d} = {correct}"
    return {
        "question": question,
        "choices": {chr(65+i): str(choices[i]) for i in range(4)},
        "answer": answer,
        "explanation": explanation,
        "difficulty": "Easy"
    }

def generate_decimals():
    a = round(random.uniform(1,10), 2)
    b = round(random.uniform(1,10), 2)
    op = random.choice(['+', '-'])
    if op == '-':
        a, b = max(a,b), min(a,b)
    question = f"What is {a} {op} {b}?"
    if op == '+':
        correct = round(a + b, 2)
    else:
        correct = round(a - b, 2)
    choices = [correct, round(correct + random.uniform(-0.5,0.5),2), round(correct - random.uniform(-0.5,0.5),2), round(correct + random.uniform(-1,1),2)]
    random.shuffle(choices)
    answer = chr(65 + choices.index(correct))
    explanation = f"{a} {op} {b} = {correct}"
    return {
        "question": question,
        "choices": {chr(65+i): str(choices[i]) for i in range(4)},
        "answer": answer,
        "explanation": explanation,
        "difficulty": "Easy"
    }

def generate_percentages():
    percent = random.randint(10,90)
    number = random.randint(10,100)
    question = f"What is {percent}% of {number}?"
    correct = (percent / 100) * number
    choices = [correct, correct + random.randint(1,10), correct - random.randint(1,10), correct * 2]
    random.shuffle(choices)
    answer = chr(65 + choices.index(correct))
    explanation = f"{percent}% of {number} = ({percent}/100) * {number} = {correct}"
    return {
        "question": question,
        "choices": {chr(65+i): str(choices[i]) for i in range(4)},
        "answer": answer,
        "explanation": explanation,
        "difficulty": "Medium"
    }

def generate_ratios():
    a = random.randint(1,10)
    b = random.randint(1,10)
    c = random.randint(1,10)
    question = f"If the ratio of A to B is {a}:{b}, and A is {a*c}, what is B?"
    correct = b * c
    choices = [correct, correct + random.randint(1,5), correct - random.randint(1,5), correct * 2]
    random.shuffle(choices)
    answer = chr(65 + choices.index(correct))
    explanation = f"Since A:B = {a}:{b}, B = (B/A)*A = ({b}/{a}) * {a*c} = {correct}"
    return {
        "question": question,
        "choices": {chr(65+i): str(choices[i]) for i in range(4)},
        "answer": answer,
        "explanation": explanation,
        "difficulty": "Medium"
    }

def generate_algebra():
    x = random.randint(1,10)
    const = random.randint(1,10)
    question = f"If x + {const} = {x + const + x}, what is x?"
    correct = x
    choices = [correct, correct + random.randint(1,5), correct - random.randint(1,5), const]
    random.shuffle(choices)
    answer = chr(65 + choices.index(correct))
    explanation = f"x + {const} = {x + const + x} => x = {x}"
    return {
        "question": question,
        "choices": {chr(65+i): str(choices[i]) for i in range(4)},
        "answer": answer,
        "explanation": explanation,
        "difficulty": "Medium"
    }

def generate_exponents():
    base = random.randint(2,5)
    exp = random.randint(2,4)
    question = f"What is {base}^{exp}?"
    correct = base ** exp
    choices = [correct, correct + random.randint(1,10), correct - random.randint(1,10), base * exp]
    random.shuffle(choices)
    answer = chr(65 + choices.index(correct))
    explanation = f"{base}^{exp} = {correct}"
    return {
        "question": question,
        "choices": {chr(65+i): str(choices[i]) for i in range(4)},
        "answer": answer,
        "explanation": explanation,
        "difficulty": "Hard"
    }

def generate_word_problems():
    # Simple word problem
    items = random.randint(5,20)
    price = random.randint(1,10)
    question = f"A store sells {items} items at ${price} each. What is the total cost?"
    correct = items * price
    choices = [correct, correct + random.randint(1,10), correct - random.randint(1,10), items + price]
    random.shuffle(choices)
    answer = chr(65 + choices.index(correct))
    explanation = f"Total cost = {items} * ${price} = ${correct}"
    return {
        "question": question,
        "choices": {chr(65+i): str(choices[i]) for i in range(4)},
        "answer": answer,
        "explanation": explanation,
        "difficulty": "Hard"
    }

def generate_arithmetic():
    generators = [
        generate_basic_operations,
        generate_fractions,
        generate_decimals,
        generate_percentages,
        generate_ratios,
        generate_algebra,
        generate_exponents,
        generate_word_problems
    ]
    lessons = {}
    pinesat_index = 0
    def normalize_question(q):
        # ensure type is set and consistent
        if 'type' not in q or q['type'] == 'multiple-choice':
            q['type'] = 'multiple-choice'
        # convert choices dict to list if necessary
        if isinstance(q.get('choices'), dict):
            q['choices'] = [q['choices'].get(ch, '') for ch in ['A', 'B', 'C', 'D']]
        # convert answer from letter to index
        if isinstance(q.get('answer'), str):
            if q['answer'] in 'ABCD':
                q['answer'] = 'ABCD'.index(q['answer'])
            else:
                try:
                    q['answer'] = int(q['answer'])
                except:
                    pass
        return q

    for lesson in range(1, 11):
        questions = []
        for i in range(20):
            # Occasionally include a Pinesat question
            if random.random() < 0.1 and pinesat_index < len(pinesat_questions):  # 10% chance
                q = pinesat_questions[pinesat_index]
                pinesat_index += 1
            else:
                gen = random.choice(generators)
                q = gen()
                # Adjust difficulty based on lesson
                if lesson <= 3:
                    q["difficulty"] = "Easy"
                elif lesson <= 6:
                    q["difficulty"] = "Medium"
                else:
                    q["difficulty"] = "Hard"
            q = normalize_question(q)
            questions.append(q)
        # Sort questions by difficulty within lesson (Easy, Medium, Hard)
        questions.sort(key=lambda x: ['Easy', 'Medium', 'Hard'].index(x['difficulty']))
        lessons[str(lesson)] = questions
    return lessons

if __name__ == "__main__":
    data = generate_arithmetic()
    print(json.dumps(data, indent=2))