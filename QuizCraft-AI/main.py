import random
import string
import os
from dotenv import load_dotenv

# Load .env file FIRST before anything else
load_dotenv()

# Import all modules
from pdf_extraction import extract_text
from chunk_text import chunk_text
from clean_text import clean_text
from quiz_gen import generate_mcqs
from stor_age import init_storage, save_quiz, load_quiz, save_result
from run import c_deadline, run
from dashboard import show_dashboard

# ── FIX 1: Import google.genai only ONCE ──────────────────────
from google import genai

# ── FIX 2: Get API key from .env, NOT hardcoded ───────────────
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("WARNING: GOOGLE_API_KEY not found in .env file.")
    print("Create a .env file with: GOOGLE_API_KEY=your_key_here")

# ── FIX 3: Do NOT call the API at top level ───────────────────
# The old code was calling client.models.generate_content() HERE
# which means EVERY run hits the API before the user even does anything.
# We move client creation INSIDE the function that needs it.

def init_client():
    return genai.Client(api_key=API_KEY)

def make_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def create():
    init_storage()
    client = init_client()

    file = input("PDF path: ").strip().strip('"').strip("'")

    try:
        start = int(input("Start page: "))
        end = int(input("End page: "))
        num_q = int(input("Number of questions: "))
        marks = int(input("Marks per question: "))
    except ValueError:
        print("Invalid input. Please enter numbers only.")
        return

    deadline = input("Deadline (YYYY-MM-DD HH:MM): ").strip()

    text = extract_text(file, start, end)
    if not text:
        print("Failed to extract text. Check the PDF path and page range.")
        return

    chunks = chunk_text(clean_text(text))
    quiz = []

    for chunk in chunks:
        if len(quiz) >= num_q:
            break

        new_qs = generate_mcqs(chunk, min(3, num_q - len(quiz)), client)
        if new_qs:
            quiz.extend(new_qs)

        print(f"Generated {len(quiz)}/{num_q}")

    if not quiz:
        print("Failed to generate quiz. Check your API key and quota.")
        return

    quiz_id = make_id()
    save_quiz(quiz_id, quiz[:num_q], marks, deadline)
    print(f"\nQuiz created! ID: {quiz_id}")

def attempt():
    quiz_id = input("Quiz ID: ").strip()
    data = load_quiz(quiz_id)

    if not data:
        print("Quiz not found.")
        return

    if not c_deadline(data["deadline"]):
        print("Deadline has passed.")
        return

    username = input("Your name: ").strip()
    score, total = run(data, username)
    save_result(username, quiz_id, score, total)

# ── Entry Point ───────────────────────────────────────────────
mode = input("Mode (create / attempt / dashboard): ").strip().lower()

if mode == "create":
    create()
elif mode == "attempt":
    attempt()
elif mode == "dashboard":
    show_dashboard(input("Quiz ID: ").strip())
else:
    print(f"Unknown mode: '{mode}'. Choose: create / attempt / dashboard")
#    C:\Users\Admin\Downloads\CO_VIVA.pdf
#         2026-04-16 11:00