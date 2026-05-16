import json
import os
import csv
from datetime import datetime

# ── FIX: Use absolute paths based on THIS file's location ─────
# Old code used "data/quizzes.json" which only works if you run
# the script from exactly the right folder.
# os.path.dirname(__file__) always gives the folder this file is in.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
QUIZ_FILE = os.path.join(DATA_DIR, "quizzes.json")
RESULTS_FILE = os.path.join(DATA_DIR, "results.csv")

def init_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE, "w") as f:
            json.dump({}, f)

def save_quiz(quiz_id, quiz, marks, deadline):
    try:
        with open(QUIZ_FILE) as f:
            db = json.load(f)
    except:
        db = {}
    db[quiz_id] = {"quiz": quiz, "marks": marks, "deadline": deadline}
    with open(QUIZ_FILE, "w") as f:
        json.dump(db, f, indent=4)

def load_quiz(quiz_id):
    try:
        with open(QUIZ_FILE) as f:
            return json.load(f).get(quiz_id)
    except:
        return None

def save_result(username, quiz_id, score, total):
    with open(RESULTS_FILE, "a", newline="") as f:
        csv.writer(f).writerow(
            [username, quiz_id, score, total, datetime.now()]
        )
