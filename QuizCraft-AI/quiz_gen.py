import time
import json
import re


def generate_mcqs(text, num_q, client):

    prompt = f"""
Generate EXACTLY {num_q} multiple choice questions.

Difficulty:
- Medium level (not too easy, not too difficult)
- Questions should test understanding, not just memorization
- Avoid overly complex or multi-layered questions

Question Style:
- Keep questions short and clear (1–3 lines max)
- Do NOT include phrases like "the text says", "according to the passage", etc.
- Ask direct, standalone questions understandable without context reference
- Focus on key concepts and practical understanding

Content:
- Prefer conceptual or reasoning-based questions
- Avoid very generic questions, but keep them accessible
- Do not make questions unnecessarily tricky

Options:
- Provide 4 options (A, B, C, D)
- All options should be plausible and similar in structure
- Avoid obviously wrong answers

Answer Distribution:
- Distribute correct answers across A, B, C, and D
- Avoid repeating the same option multiple times in a row

Answer:
- Must be one of A, B, C, or D
- Must be clearly correct

Return ONLY valid JSON. No explanation. No markdown. No code block.

Format:
[
  {{
    "question": "string",
    "options": {{
      "A": "string",
      "B": "string",
      "C": "string",
      "D": "string"
    }},
    "answer": "A"
  }}
]

TEXT:
{text[:1000]}
"""

    max_retries = 5
    base_delay = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            raw = response.text.strip() if hasattr(response, "text") else str(response)

            # Remove markdown if present
            raw = re.sub(r"```json\s*", "", raw)
            raw = re.sub(r"```\s*", "", raw)
            raw = raw.strip()

            # Extract JSON array
            match = re.search(r"\[\s*\{.*?\}\s*\]", raw, re.DOTALL)
            if not match:
                raise ValueError("No JSON array found in response")

            data = json.loads(match.group(0))

            if not isinstance(data, list):
                raise ValueError("Response is not a list")

            valid_mcqs = []

            for q in data:
                if (
                    isinstance(q, dict)
                    and "question" in q
                    and "options" in q
                    and "answer" in q
                    and isinstance(q["options"], dict)
                    and set(q["options"].keys()) == {"A", "B", "C", "D"}
                    and q["answer"] in {"A", "B", "C", "D"}
                    and len(q["question"].strip()) > 5
                ):
                    valid_mcqs.append(q)

            if valid_mcqs:
                return valid_mcqs

            raise ValueError("No valid MCQs in response")

        except Exception as e:
            wait = base_delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed: {e}")

            if (
                "429" in str(e)
                or "quota" in str(e).lower()
                or "RESOURCE_EXHAUSTED" in str(e)
            ):
                print("Quota exhausted. Wait 24 hours or create a new Google Cloud Project.")
                return []

            print(f"Retrying in {wait}s...")
            time.sleep(wait)

    print("All retries failed.")
    return []