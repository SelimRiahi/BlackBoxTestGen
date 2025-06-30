import pdfplumber
import ollama
import os
from textwrap import dedent

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def generate_gherkin(pdf_path):
    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("No text extracted from PDF")
        return

    # Build prompt
    prompt = dedent(f"""
You are a senior QA engineer specialized in black-box testing and Behavior-Driven Development (BDD).

Given vague or partial software requirements, generate clean and logical Gherkin `.feature` files for automated testing.

Follow these strict rules:

---

STRUCTURE RULES:

1. Each `Feature:` should describe a single functional capability of the system.
2. Each `Scenario:` must include:
   - `Given`: Describe the user's initial state and the correct page they are on (e.g., "the user is on the registration page"). Do not use endpoints or page URLs. The page name must match the scenario purpose (e.g., registration vs login).
   - `When`: Combine all user actions into one step (e.g., "the user fills in the registration form and submits it"). Do not split into multiple small actions. Do not use sample data or example values.
   - `Then` and `And`: Describe only **observable and logical outcomes**, such as:
     - User-facing success or error messages
     - HTTP response status codes (e.g., 200, 400)

---

CONTENT RULES:

- Do not include quoted values, example usernames, HTML, or raw JSON.
- Do not mention redirects, frontend navigation, backend logic, or implementation details.
- Only describe results that are logical and observable from the user's perspective.
- The outcomes described in Then/And steps must be relevant and logical for the scenario context.
- Do not mention any results that are typically associated with different user flows or steps.
  For example, do not mention login outcomes in registration scenarios, or vice versa.
- Do not include internal objects (like tokens, session IDs, or data structures) unless they are explicitly part of the API response and directly relevant to test verification.
- Use logical reasoning to ensure the scenario steps are consistent, realistic, and appropriate for the described user action.
- Avoid including outcomes that do not logically follow from the scenario context or user flow.---



- Output only clean Gherkin syntax with no explanation.
- Do not add markdown code blocks (like ```gherkin).
- Do not include headings or extra commentary.
---

Now, based on the following requirement, generate:
- A `Feature:`
- One or more `Scenario:` blocks

    System specification:
    \"\"\"
    {text[:5000]}
    \"\"\"
    """)

    print("Generating test scenarios...")

    try:
        response = ollama.generate(
            model="llama3.1",
            prompt=prompt,
            options={"temperature": 0}
        )

        os.makedirs("features", exist_ok=True)
        with open("features/test_scenarios.feature", "w", encoding="utf-8") as f:
            f.write(response['response'])

        print("✅ Successfully generated test_scenarios.feature")

    except Exception as e:
        print(f"❌ Ollama generation failed: {e}")

# Execute
if __name__ == "__main__":
    pdf_path = r"docs/cahier1.pdf"
    generate_gherkin(pdf_path)
