import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import csv
import random
import string

# ── Make sure all sibling modules are importable ──────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from pdf_extraction import extract_text
from chunk_text import chunk_text
from clean_text import clean_text
from quiz_gen import generate_mcqs
from stor_age import init_storage, save_quiz, load_quiz, save_result
from run import c_deadline
from google import genai

API_KEY = os.getenv("GOOGLE_API_KEY")

# ════════════════════════════════════════════════════════════════
#  DESIGN TOKENS
# ════════════════════════════════════════════════════════════════
BG      = "#0F172A"   # deep navy background
CARD    = "#1E293B"   # card surface
BORDER  = "#334155"   # subtle borders / muted inputs
INDIGO  = "#6366F1"   # primary accent
INDIGO2 = "#4F46E5"   # primary hover
GREEN   = "#22C55E"   # success
RED     = "#EF4444"   # error / fail
AMBER   = "#F59E0B"   # warning / rank 1
BLUE    = "#38BDF8"   # rank 2
TEXT    = "#F1F5F9"   # primary text
MUTED   = "#94A3B8"   # secondary text
WHITE   = "#FFFFFF"

FH  = ("Segoe UI", 26, "bold")   # hero heading
FT  = ("Segoe UI", 18, "bold")   # page title
FB  = ("Segoe UI", 11)           # body
FS  = ("Segoe UI", 9)            # small / label
FM  = ("Consolas", 13, "bold")   # monospace (quiz ID)

# ════════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════════
def make_id():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


def btn(parent, text, cmd, bg=INDIGO, fg=WHITE, w=20, py=10, font=None):
    """Flat, hover-aware button factory."""
    f = font or ("Segoe UI", 11, "bold")
    hover = INDIGO2 if bg == INDIGO else BORDER
    b = tk.Button(parent, text=text, command=cmd,
                  bg=bg, fg=fg, activebackground=hover, activeforeground=WHITE,
                  relief="flat", cursor="hand2", width=w,
                  padx=14, pady=py, font=f, bd=0)
    b.bind("<Enter>", lambda e: b.config(bg=hover))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def entry(parent, var, width=30, show=""):
    """Styled entry widget."""
    return tk.Entry(parent, textvariable=var, bg=BORDER, fg=TEXT,
                    insertbackground=TEXT, relief="flat",
                    font=FB, width=width, show=show)


def lbl(parent, text, fg=TEXT, font=FB, **kw):
    kw.setdefault("bg", parent["bg"])
    return tk.Label(parent, text=text, fg=fg, font=font, **kw)


def section_label(parent, text):
    lbl(parent, text, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(
        anchor="w", pady=(10, 3))


# ════════════════════════════════════════════════════════════════
#  MAIN APPLICATION WINDOW
# ════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QuizCraft AI")
        self.geometry("960x660")
        self.minsize(820, 580)
        self.configure(bg=BG)

        self._build_sidebar()

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        init_storage()

        self.frames = {}
        for Cls in (HomePage, CreatePage, AttemptPage, DashboardPage):
            f = Cls(self.content, self)
            self.frames[Cls.__name__] = f
            f.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show("HomePage")

    # ── Sidebar ───────────────────────────────────────────────
    def _build_sidebar(self):
        sb = tk.Frame(self, bg=CARD, width=210)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Brand
        brand = tk.Frame(sb, bg=CARD)
        brand.pack(fill="x", pady=(32, 16), padx=24)
        lbl(brand, "⚡", fg=INDIGO, font=("Segoe UI", 30)).pack()
        lbl(brand, "QuizCraft AI", fg=TEXT, font=("Segoe UI", 15, "bold")).pack()
        lbl(brand, "Powered by Gemini", fg=MUTED, font=FS).pack()

        tk.Frame(sb, bg=BORDER, height=1).pack(fill="x", padx=20, pady=8)

        nav = [
            ("🏠   Home",         "HomePage"),
            ("➕   Create Quiz",   "CreatePage"),
            ("📝   Attempt Quiz",  "AttemptPage"),
            ("📊   Dashboard",     "DashboardPage"),
        ]
        self._nav = {}
        for label, page in nav:
            b = tk.Button(sb, text=label, bg=CARD, fg=TEXT,
                          activebackground=INDIGO, activeforeground=WHITE,
                          relief="flat", cursor="hand2", anchor="w",
                          padx=22, pady=11, font=("Segoe UI", 11),
                          command=lambda p=page: self.show(p))
            b.pack(fill="x")
            self._nav[page] = b

        tk.Frame(sb, bg=BORDER, height=1).pack(fill="x", padx=20, side="bottom", pady=8)
        lbl(sb, "v1.0  •  AI Edition", fg=MUTED, font=FS).pack(side="bottom", pady=10)

    def show(self, name):
        for n, b in self._nav.items():
            b.config(bg=INDIGO if n == name else CARD,
                     fg=WHITE if n == name else TEXT)
        self.frames[name].tkraise()
        if hasattr(self.frames[name], "on_show"):
            self.frames[name].on_show()


# ════════════════════════════════════════════════════════════════
#  HOME PAGE
# ════════════════════════════════════════════════════════════════
class HomePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        pad = tk.Frame(self, bg=BG)
        pad.pack(fill="x", padx=44, pady=(44, 8))
        lbl(pad, "Welcome to QuizCraft AI", fg=TEXT, font=FH).pack(anchor="w")
        lbl(pad, "Generate AI-powered quizzes from any PDF in seconds.",
            fg=MUTED, font=FB).pack(anchor="w", pady=(6, 0))

        # Feature cards
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=44, pady=28)

        cards = [
            ("➕", "Create Quiz",
             "Upload a PDF and let Gemini\ncraft smart MCQs for you.", GREEN,  "CreatePage"),
            ("📝", "Attempt Quiz",
             "Enter a quiz ID and test your\nknowledge before the deadline.", INDIGO, "AttemptPage"),
            ("📊", "Dashboard",
             "View rankings and scores\nfor any quiz by ID.", AMBER,  "DashboardPage"),
        ]
        for i, (icon, title, desc, color, page) in enumerate(cards):
            c = tk.Frame(row, bg=CARD, cursor="hand2")
            c.grid(row=0, column=i, padx=10, sticky="nsew")
            row.columnconfigure(i, weight=1)

            lbl(c, icon, fg=color, font=("Segoe UI", 34)).pack(pady=(26, 6))
            lbl(c, title, fg=TEXT, font=("Segoe UI", 13, "bold")).pack()
            lbl(c, desc, fg=MUTED, font=FS, justify="center").pack(
                pady=(6, 26), padx=16)

            for w in [c] + c.winfo_children():
                w.bind("<Button-1>", lambda e, p=page: self.app.show(p))

            def _enter(e, fr=c, col=color):
                fr.config(bg=col)
                for w in fr.winfo_children():
                    w.config(bg=col)

            def _leave(e, fr=c):
                fr.config(bg=CARD)
                for w in fr.winfo_children():
                    w.config(bg=CARD)

            c.bind("<Enter>", _enter)
            c.bind("<Leave>", _leave)

        # Info tip
        tip = tk.Frame(self, bg=CARD)
        tip.pack(fill="x", padx=44, pady=4)
        lbl(tip, "💡  Quick Tip", fg=AMBER,
            font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=22, pady=(16, 4))
        lbl(tip, "Ensure your GOOGLE_API_KEY is set in the .env file before creating quizzes."
                 "  Free tier: Gemini Flash.",
            fg=MUTED, font=FB).pack(anchor="w", padx=22, pady=(0, 16))

        # API key status
        status_row = tk.Frame(self, bg=BG)
        status_row.pack(fill="x", padx=44, pady=(8, 0))
        if API_KEY:
            lbl(status_row, "✅  API key loaded", fg=GREEN, font=FB).pack(anchor="w")
        else:
            lbl(status_row, "⚠️  No API key found in .env — quiz creation will fail.",
                fg=RED, font=FB).pack(anchor="w")


# ════════════════════════════════════════════════════════════════
#  CREATE PAGE  — FIX: generates EXACTLY num_q questions
# ════════════════════════════════════════════════════════════════
class CreatePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._last_quiz_id = None
        self._build()

    def _build(self):
        h = tk.Frame(self, bg=BG)
        h.pack(fill="x", padx=44, pady=(36, 4))
        lbl(h, "Create Quiz", fg=TEXT, font=FT).pack(anchor="w")
        lbl(h, "Upload a PDF and let Gemini generate MCQs automatically.",
            fg=MUTED, font=FS).pack(anchor="w")

        card = tk.Frame(self, bg=CARD)
        card.pack(fill="both", expand=True, padx=44, pady=16)
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── PDF path ──────────────────────────────────────────
        section_label(inner, "PDF FILE")
        pdf_row = tk.Frame(inner, bg=CARD)
        pdf_row.pack(fill="x")
        self.pdf_var = tk.StringVar()
        entry(pdf_row, self.pdf_var, width=46).pack(
            side="left", fill="x", expand=True, ipady=7, padx=(0, 10))
        btn(pdf_row, "Browse …", self._browse,
            bg=BORDER, w=12, py=7).pack(side="right")

        # ── Numeric inputs ────────────────────────────────────
        grid = tk.Frame(inner, bg=CARD)
        grid.pack(fill="x", pady=14)
        labels   = ["START PAGE", "END PAGE", "# QUESTIONS", "MARKS / Q"]
        defaults = [1, 5, 10, 1]
        self._spins = []
        for i, (lab, default) in enumerate(zip(labels, defaults)):
            f = tk.Frame(grid, bg=CARD)
            f.grid(row=0, column=i, padx=6, sticky="ew")
            grid.columnconfigure(i, weight=1)
            lbl(f, lab, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
            var = tk.IntVar(value=default)
            ttk.Spinbox(f, from_=1, to=999, textvariable=var, width=10).pack(
                anchor="w", ipady=4)
            self._spins.append(var)

        # ── Deadline ──────────────────────────────────────────
        section_label(inner, "DEADLINE  (YYYY-MM-DD HH:MM)")
        self.dl_var = tk.StringVar(value="2030-12-31 23:59")
        entry(inner, self.dl_var, width=24).pack(anchor="w", ipady=7)

        # ── Progress area ─────────────────────────────────────
        self.prog_frame = tk.Frame(inner, bg=CARD)
        self.prog_frame.pack(fill="x", pady=(14, 0))
        self.prog_lbl = lbl(self.prog_frame, "", fg=GREEN, font=("Segoe UI", 10))
        self.prog_lbl.pack(anchor="w")
        self.progress = ttk.Progressbar(self.prog_frame, mode="indeterminate",
                                        length=400)

        # ── Generate button ───────────────────────────────────
        btn_row = tk.Frame(inner, bg=CARD)
        btn_row.pack(fill="x", pady=(14, 0))
        self.gen_btn = btn(btn_row, "⚡  Generate Quiz", self._generate,
                           bg=INDIGO, w=24, py=12,
                           font=("Segoe UI", 12, "bold"))
        self.gen_btn.pack(side="left")

        # ── Result area with Copy button ──────────────────────
        self.result_outer = tk.Frame(inner, bg=CARD)
        self.result_outer.pack(anchor="w", pady=(14, 0), fill="x")

        self.result_lbl = lbl(self.result_outer, "", fg=GREEN,
                              font=("Segoe UI", 12, "bold"))
        self.result_lbl.pack(side="left")

        # Copy-ID button — hidden until a quiz is created
        self.copy_btn = tk.Button(
            self.result_outer,
            text="📋 Copy ID",
            command=self._copy_id,
            bg=AMBER, fg="#0F172A",
            activebackground="#D97706", activeforeground=WHITE,
            relief="flat", cursor="hand2",
            padx=12, pady=4,
            font=("Segoe UI", 10, "bold"), bd=0
        )
        # shown only after success

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select PDF", filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf_var.set(path)

    def _copy_id(self):
        if self._last_quiz_id:
            self.clipboard_clear()
            self.clipboard_append(self._last_quiz_id)
            # flash feedback
            orig = self.copy_btn["text"]
            self.copy_btn.config(text="✅ Copied!")
            self.after(1500, lambda: self.copy_btn.config(text=orig))

    def _generate(self):
        pdf_path = self.pdf_var.get().strip().strip('"').strip("'")
        start, end, num_q, marks = [v.get() for v in self._spins]
        deadline = self.dl_var.get().strip()

        if not pdf_path:
            messagebox.showerror("Missing", "Please select a PDF file.")
            return
        if not os.path.exists(pdf_path):
            messagebox.showerror("Not Found", f"File not found:\n{pdf_path}")
            return
        if start < 1 or end < start:
            messagebox.showerror("Invalid Range", "End page must be ≥ Start page.")
            return
        if num_q < 1:
            messagebox.showerror("Invalid", "Number of questions must be ≥ 1.")
            return

        self.gen_btn.config(state="disabled", text="Generating…")
        self.result_lbl.config(text="")
        self.copy_btn.pack_forget()
        self._set_prog("📄  Extracting text from PDF…")
        self.progress.pack(fill="x")
        self.progress.start(10)

        def worker():
            try:
                text = extract_text(pdf_path, start, end)
                if not text:
                    self._err("Could not extract text. Check the page range.")
                    return

                self._set_prog("🔧  Cleaning and chunking text…")
                chunks = chunk_text(clean_text(text))

                self._set_prog(f"🤖  Calling Gemini AI…  (0 / {num_q} questions)")
                client = genai.Client(api_key=API_KEY)
                quiz = []

                # ── FIX: ask for ALL remaining questions per chunk ──
                # Old code: generate_mcqs(chunk, min(3, …), client)
                #   → always ≤ 3 per call → 10 questions becomes 9
                # New code: ask for exactly (num_q - len(quiz)) per call
                #   → fills up to the exact number requested
                for chunk in chunks:
                    if len(quiz) >= num_q:
                        break
                    needed = num_q - len(quiz)          # how many still needed
                    new_qs = generate_mcqs(chunk, needed, client)
                    if new_qs:
                        quiz.extend(new_qs)
                    self._set_prog(
                        f"🤖  Calling Gemini AI…  ({len(quiz)} / {num_q} questions)")

                if not quiz:
                    self._err("No questions generated.\n"
                              "Check your API key and quota.")
                    return

                quiz_id = make_id()
                save_quiz(quiz_id, quiz[:num_q], marks, deadline)
                self._ok(quiz_id, len(quiz[:num_q]))

            except Exception as ex:
                self._err(str(ex))

        threading.Thread(target=worker, daemon=True).start()

    def _set_prog(self, msg):
        self.after(0, lambda: self.prog_lbl.config(text=msg))

    def _ok(self, quiz_id, count):
        def _do():
            self._last_quiz_id = quiz_id
            self.progress.stop()
            self.progress.pack_forget()
            self.prog_lbl.config(text="")
            self.gen_btn.config(state="normal", text="⚡  Generate Quiz")
            self.result_lbl.config(
                text=f"✅  Quiz created  ({count} questions)    ID: {quiz_id}",
                fg=GREEN)
            self.copy_btn.pack(side="left", padx=(16, 0))
            # also silently copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(quiz_id)
        self.after(0, _do)

    def _err(self, msg):
        def _do():
            self.progress.stop()
            self.progress.pack_forget()
            self.prog_lbl.config(text="")
            self.gen_btn.config(state="normal", text="⚡  Generate Quiz")
            messagebox.showerror("Error", msg)
        self.after(0, _do)


# ════════════════════════════════════════════════════════════════
#  ATTEMPT PAGE
# ════════════════════════════════════════════════════════════════
class AttemptPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build_login()

    def _build_login(self):
        self.login_f = tk.Frame(self, bg=BG)
        self.login_f.place(relx=0.5, rely=0.48, anchor="center")

        lbl(self.login_f, "📝  Attempt Quiz", fg=TEXT, font=FT).pack(pady=(0, 28))

        card = tk.Frame(self.login_f, bg=CARD)
        card.pack(ipadx=36, ipady=28)

        section_label(card, "QUIZ ID")
        self.qid_var = tk.StringVar()
        entry(card, self.qid_var, width=30).pack(ipady=7)

        section_label(card, "YOUR NAME")
        self.name_var = tk.StringVar()
        entry(card, self.name_var, width=30).pack(ipady=7)

        btn(card, "Start Quiz →", self._start,
            bg=INDIGO, w=30, py=11,
            font=("Segoe UI", 11, "bold")).pack(pady=(22, 0))

        self.quiz_f = tk.Frame(self, bg=BG)

    def _start(self):
        qid  = self.qid_var.get().strip()
        name = self.name_var.get().strip()
        if not qid or not name:
            messagebox.showerror("Missing", "Enter both Quiz ID and your name.")
            return
        data = load_quiz(qid)
        if not data:
            messagebox.showerror("Not Found", f"No quiz found with ID: {qid}")
            return
        if not c_deadline(data["deadline"]):
            messagebox.showerror("Deadline Passed",
                                 f"This quiz expired on:\n{data['deadline']}")
            return
        self._run_quiz(data, name, qid)

    def _run_quiz(self, data, username, quiz_id):
        self.login_f.place_forget()
        for w in self.quiz_f.winfo_children():
            w.destroy()
        self.quiz_f.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._quiz     = data["quiz"]
        self._marks    = data["marks"]
        self._username = username
        self._quiz_id  = quiz_id
        self._cur      = 0
        self._answers  = {}
        self._ans_var  = tk.StringVar()

        hbar = tk.Frame(self.quiz_f, bg=CARD)
        hbar.pack(fill="x")
        lbl(hbar, f"Quiz  {quiz_id}", fg=TEXT,
            font=("Segoe UI", 12, "bold")).pack(side="left", padx=22, pady=13)
        self.ctr_lbl = lbl(hbar, "", fg=MUTED, font=FB)
        self.ctr_lbl.pack(side="right", padx=22)

        self.step_bar = ttk.Progressbar(self.quiz_f, maximum=len(self._quiz))
        self.step_bar.pack(fill="x")

        self.q_area = tk.Frame(self.quiz_f, bg=BG)
        self.q_area.pack(fill="both", expand=True, padx=70, pady=28)

        self._show_q()

    def _show_q(self):
        for w in self.q_area.winfo_children():
            w.destroy()

        i = self._cur
        q = self._quiz[i]
        total = len(self._quiz)

        self.ctr_lbl.config(text=f"Question {i+1} / {total}")
        self.step_bar["value"] = i + 1

        qcard = tk.Frame(self.q_area, bg=CARD)
        qcard.pack(fill="x")
        lbl(qcard, f"Q{i+1}.", fg=MUTED,
            font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=22, pady=(18, 0))
        lbl(qcard, q["question"], fg=TEXT,
            font=("Segoe UI", 13), wraplength=640,
            justify="left").pack(anchor="w", padx=22, pady=(4, 18))

        self._ans_var.set(self._answers.get(i, ""))
        options = q["options"]
        if isinstance(options, list) and len(options) == 4:
            options = dict(zip("ABCD", options))

        for key, val in options.items():
            opt_f = tk.Frame(self.q_area, bg=CARD, cursor="hand2")
            opt_f.pack(fill="x", pady=5)

            def _pick(e, k=key):
                self._ans_var.set(k)

            rb = tk.Radiobutton(opt_f,
                                text=f"  {key}.   {val}",
                                variable=self._ans_var, value=key,
                                bg=CARD, fg=TEXT,
                                selectcolor=INDIGO,
                                activebackground=CARD,
                                activeforeground=TEXT,
                                font=("Segoe UI", 11),
                                relief="flat")
            rb.pack(anchor="w", padx=18, pady=11, fill="x")
            opt_f.bind("<Button-1>", _pick)
            rb.bind("<Button-1>",    _pick)

        nav = tk.Frame(self.q_area, bg=BG)
        nav.pack(fill="x", pady=(18, 0))

        if i > 0:
            btn(nav, "← Back", self._prev, bg=BORDER, w=13, py=9).pack(side="left")

        is_last = (i == total - 1)
        label = "Submit ✓" if is_last else "Next →"
        color = GREEN      if is_last else INDIGO
        btn(nav, label, self._next_or_submit,
            bg=color, w=15, py=9,
            font=("Segoe UI", 11, "bold")).pack(side="right")

    def _prev(self):
        self._answers[self._cur] = self._ans_var.get()
        self._cur -= 1
        self._show_q()

    def _next_or_submit(self):
        self._answers[self._cur] = self._ans_var.get()
        if self._cur < len(self._quiz) - 1:
            self._cur += 1
            self._show_q()
        else:
            self._submit()

    def _submit(self):
        missing = [i + 1 for i in range(len(self._quiz))
                   if not self._answers.get(i)]
        if missing:
            ok = messagebox.askyesno(
                "Unanswered Questions",
                f"Question(s) {missing} are unanswered.\nSubmit anyway?")
            if not ok:
                return

        score = sum(
            self._marks
            for i, q in enumerate(self._quiz)
            if self._answers.get(i) == q["answer"]
        )
        total = self._marks * len(self._quiz)
        save_result(self._username, self._quiz_id, score, total)
        self._show_result(score, total)

    def _show_result(self, score, total):
        for w in self.quiz_f.winfo_children():
            w.destroy()

        pct   = round(score / total * 100) if total else 0
        color = GREEN if pct >= 60 else AMBER if pct >= 40 else RED
        icon  = "🎉" if pct >= 60 else "😐" if pct >= 40 else "😔"
        grade = "Excellent!" if pct >= 80 else \
                "Good job!"  if pct >= 60 else \
                "Keep going!" if pct >= 40 else \
                "Need more practice."
        pass_fail = "PASS" if pct >= 50 else "FAIL"

        center = tk.Frame(self.quiz_f, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        lbl(center, icon, fg=color, font=("Segoe UI", 50)).pack()
        lbl(center, "Quiz Complete!", fg=TEXT, font=FT).pack(pady=(10, 2))
        lbl(center, self._username, fg=MUTED, font=("Segoe UI", 13)).pack()
        lbl(center, grade, fg=color, font=("Segoe UI", 11, "italic")).pack(pady=(4, 0))

        scard = tk.Frame(center, bg=CARD)
        scard.pack(pady=24, ipadx=48, ipady=22)
        lbl(scard, f"{score} / {total}", fg=color,
            font=("Segoe UI", 42, "bold")).pack()
        lbl(scard, f"{pct}%   •   {pass_fail}",
            fg=MUTED, font=("Segoe UI", 12)).pack(pady=(4, 0))

        def _back():
            self.quiz_f.place_forget()
            self.login_f.place(relx=0.5, rely=0.48, anchor="center")
            self.qid_var.set("")
            self.name_var.set("")

        def _dashboard():
            self.app.frames["DashboardPage"].qid_var.set(self._quiz_id)
            self.app.frames["DashboardPage"]._load()
            self.app.show("DashboardPage")

        row = tk.Frame(center, bg=BG)
        row.pack()
        btn(row, "Take Another Quiz", _back,
            bg=BORDER, w=20, py=9).pack(side="left", padx=6)
        btn(row, "View Leaderboard →", _dashboard,
            bg=INDIGO, w=20, py=9).pack(side="left", padx=6)


# ════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE
# ════════════════════════════════════════════════════════════════
class DashboardPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        h = tk.Frame(self, bg=BG)
        h.pack(fill="x", padx=44, pady=(36, 8))
        lbl(h, "Dashboard", fg=TEXT, font=FT).pack(anchor="w")
        lbl(h, "View quiz results and rankings by Quiz ID.",
            fg=MUTED, font=FS).pack(anchor="w")

        sr = tk.Frame(self, bg=BG)
        sr.pack(fill="x", padx=44, pady=(10, 18))
        self.qid_var = tk.StringVar()
        entry(sr, self.qid_var, width=24).pack(
            side="left", ipady=8, padx=(0, 12))
        btn(sr, "Load Results", self._load,
            bg=INDIGO, w=16, py=8).pack(side="left")
        self.status_lbl = lbl(sr, "", fg=MUTED, font=FB)
        self.status_lbl.pack(side="left", padx=20)

        tbl_f = tk.Frame(self, bg=BG)
        tbl_f.pack(fill="both", expand=True, padx=44, pady=(0, 30))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Q.Treeview",
                        background=CARD, foreground=TEXT,
                        fieldbackground=CARD, rowheight=38,
                        font=("Segoe UI", 11), borderwidth=0)
        style.configure("Q.Treeview.Heading",
                        background=BORDER, foreground=TEXT,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Q.Treeview",
                  background=[("selected", INDIGO)],
                  foreground=[("selected", WHITE)])

        cols = ("#", "Name", "Score", "Total", "Percentage", "Attempted At")
        self.tree = ttk.Treeview(tbl_f, columns=cols, show="headings",
                                  style="Q.Treeview", height=14)
        widths = [44, 190, 80, 80, 110, 220]
        aligns = ["center", "w", "center", "center", "center", "center"]
        for col, w, a in zip(cols, widths, aligns):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor=a, minwidth=w)

        vsb = ttk.Scrollbar(tbl_f, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.tag_configure("gold",   background="#451A03", foreground=AMBER)
        self.tree.tag_configure("silver", background="#0C1A2E", foreground=BLUE)

    def _load(self):
        qid = self.qid_var.get().strip()
        if not qid:
            messagebox.showerror("Missing", "Enter a Quiz ID.")
            return

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        results_file = os.path.join(BASE_DIR, "data", "results.csv")

        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            with open(results_file, newline="") as f:
                rows = [r for r in csv.reader(f) if len(r) >= 4 and r[1] == qid]
        except FileNotFoundError:
            self.status_lbl.config(text="No results file found yet.", fg=AMBER)
            return

        if not rows:
            self.status_lbl.config(
                text=f"No attempts found for quiz: {qid}", fg=AMBER)
            return

        rows.sort(key=lambda x: int(x[2]), reverse=True)

        for rank, r in enumerate(rows, 1):
            pct_val = round(int(r[2]) / int(r[3]) * 100) if int(r[3]) > 0 else 0
            pct_str = f"{pct_val}%"
            tag     = "gold" if rank == 1 else "silver" if rank == 2 else ""
            date    = r[4] if len(r) > 4 else "—"
            self.tree.insert("", "end",
                             values=(rank, r[0], r[2], r[3], pct_str, date),
                             tags=(tag,))

        self.status_lbl.config(
            text=f"✅  {len(rows)} result(s) for quiz '{qid}'", fg=GREEN)

    def on_show(self):
        pass


# ════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
