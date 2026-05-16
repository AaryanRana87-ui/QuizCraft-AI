import csv

def show_dashboard(quiz_id):
    try:
        with open("data/results.csv") as f:
            attempts = []
            for r in csv.reader(f):
                if r[1] == quiz_id:
                    attempts.append(r) #makes a list of quiz having the same quiz id
    except FileNotFoundError:
        print("No results yet.")
        return
    if not attempts:
        print("No attempts for this quiz ID.")
        return
    print(f"\n-- Results: {quiz_id} -- ({len(attempts)} attempts)\n")

    ranking_list = sorted(attempts, key=lambda x: int(x[2]), reverse=True) #makes the list in descending order of the score
    for i, r in enumerate(ranking_list, 1):
        print(f"#{i} {r[0]:<20} {r[2]}/{r[3]}")