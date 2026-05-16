# QuizCraft AI

AI Powered PDF to Quiz Generator built using Python and Google Gemini API.

QuizCraft AI converts study PDFs into interactive MCQ based quizzes automatically. The project extracts text from PDFs, preprocesses and chunks the content, sends it to Google Gemini for question generation, and creates quizzes that students can attempt through both a CLI and a Tkinter based desktop GUI.

Developed as a second semester Python coursework project.

---

# Features

* PDF text extraction using `pdfplumber`
* AI generated MCQs using Google Gemini API
* Tkinter based desktop GUI
* Command Line Interface support
* Quiz deadlines and validation
* Unique 6 character Quiz IDs
* Real time leaderboard system
* Local JSON and CSV based storage
* Modular Python architecture

---

# Tech Stack

* Python
* Tkinter
* Google Gemini API
* pdfplumber
* JSON
* CSV

---

# Project Structure

```bash
QuizCraft-AI/
│
├── data/
│   ├── quizzes.json
│   └── results.csv
│
├── chunk_text.py
├── clean_text.py
├── dashboard.py
├── gui.py
├── main.py
├── pdf_extraction.py
├── quiz_gen.py
├── requirements.txt
├── run.py
├── stor_age.py
└── .env
```

---

# Module Overview

## main.py

Controls the overall workflow and handles mode selection between quiz creation, attempting quizzes, and leaderboard viewing.

## gui.py

Tkinter based desktop GUI containing quiz creation, quiz attempt, and leaderboard interfaces.

## pdf_extraction.py

Extracts selectable text from PDF files using `pdfplumber`.

## clean_text.py

Cleans and preprocesses extracted text by removing unwanted symbols and formatting issues.

## chunk_text.py

Splits large text into smaller chunks before sending them to the Gemini API.

## quiz_gen.py

Handles AI based MCQ generation using Google Gemini API.

## run.py

Manages quiz execution, scoring, answer checking, and deadline validation.

## dashboard.py

Displays leaderboard rankings using stored quiz results.

## stor_age.py

Handles local storage using JSON and CSV files.

---

# Workflow

1. User uploads a PDF
2. Text is extracted from selected pages
3. Text is cleaned and chunked
4. Gemini API generates MCQs
5. Quiz is stored locally with a unique ID
6. Students attempt the quiz
7. Scores are saved automatically
8. Leaderboard displays rankings

---

# GUI Screenshots

Add your GUI screenshots here.

Example:

```md

```

---

# Installation

## Clone the Repository

```bash
git clone https://github.com/yourusername/QuizCraft-AI.git
cd QuizCraft-AI
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a `.env` file and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

---

# Running the Project

## Run CLI Version

```bash
python main.py
```

## Run GUI Version

```bash
python gui.py
```

---

# Sample CLI Flow

```bash
Mode (create / attempt / dashboard): create
PDF path: sample.pdf
Start page: 1
End page: 8
Questions: 10
Deadline: 2026-04-14 11:00
```

---

# Learning Outcomes

This project helped us gain hands on experience in:

* API integration
* Prompt engineering
* GUI development
* File handling
* Modular project architecture
* Debugging and workflow integration
* Local data storage

---

# Future Improvements

* Web deployment support
* Authentication system
* Online database integration
* Analytics dashboard
* Timer based quiz attempts
* Better UI design and responsiveness

---

# Contributors

* Aaryan Rana
* Ved Waghmare
* Pushkar Mhatre
* Harsh Dalal

---

# Disclaimer

This project was developed for educational and learning purposes as part of a college Python coursework project.
