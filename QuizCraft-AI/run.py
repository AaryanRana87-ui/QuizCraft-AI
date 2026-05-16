from datetime import datetime

def c_deadline(deadline): #deadline is datetime in str type
    return datetime.now() <= datetime.strptime(deadline, "%Y-%m-%d %H:%M") #returns true or false if the current time is less than the deadline
#while comparing strptime converts the datetime from str to right format

def run(quiz_data, username):
    quiz = quiz_data["quiz"] #get every question's question options and answer
    marks = quiz_data["marks"]
    score = 0
    total = marks* len(quiz)

    for i, q in enumerate(quiz,1):
        print(f"\nQ{i}: {q['question']}")

        options = q["options"]

        # fix: convert list to dict if needed
        if isinstance(options, list) and len(options) == 4:
            options = {
                "A": options[0],
                "B": options[1],
                "C": options[2],
                "D": options[3]
            }

        # fix: correct wrong dict keys if needed
        elif isinstance(options, dict):
            if set(options.keys()) != {"A", "B", "C", "D"}:
                values = list(options.values())
                if len(values) == 4:
                    options = {
                        "A": values[0],
                        "B": values[1],
                        "C": values[2],
                        "D": values[3]
                    }

        for k,v in options.items():
            print(f" {k} {v}")

        while(True):
            ans = input("Answer (A/B/C/D) :").strip().upper()
            if ans in ["A", "B","C", "D"]:
                break
            print("Enter only A, B, C, or D only")
        
        if ans == q["answer"]:
            score += marks
            print("Correct Answer")
        else:
            print(f"Wrong Answer. Correct: {q['answer']}")

    print(f"\n{username} -> {score}/{total}")
    return score, total