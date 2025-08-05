import subprocess
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file using PyMuPDF."""
    try:
        with fitz.open(pdf_path) as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        print(f"Failed to extract PDF text: {e}")
        return ""

def build_blackbox_prompt(doc_text):
    return f"""
You are a QA engineer specializing in **black-box Gherkin scenario generation**.

You do **not** have access to the application's source code, backend, APIs, tokens (e.g., JWT), database, or any internal logic.
You are only provided with the **user-facing documentation below**, which simulates what a user can observe or interact with.

Your task is to infer and generate **realistic black-box Gherkin scenarios** based solely on visible features and UI behavior.

✅ Rules:
- Never mention JWT tokens, localStorage, session storage, cookies, backend requests, internal state, or API endpoints.
- Never reference any implementation logic or make assumptions about technologies used.
- Generate tests only from the perspective of a user: UI elements, visible content, inputs, buttons, navigation, and results.
- For every user-visible interactive control (such as buttons, toggles, or links) described or implied by the documentation, generate at least one scenario reflecting typical user interaction and outcome.
- Avoid explicitly naming controls or UI elements by internal or technical terms.
- Describe only user actions and observable outcomes from the user perspective.
- For each feature, generate:
    - One valid (passing) scenario showing correct user behavior
    - One invalid (failing) or edge-case scenario showing misuse or error
- Use **natural language variation** in `Given`, `When`, `Then` steps to avoid repetition.
- Never invent features not described in the documentation.
- Use clean and distinct scenarios — no redundant phrasing or copy/paste patterns.

📄 Use this format for each feature:

Feature: <User-facing feature name>

  Scenario: <Successful case>
    Given ...
    When ...
    Then ...

  Scenario: <Failure or edge case>
    Given ...
    When ...
    Then ...

Documentation:
\"\"\"
{doc_text}
\"\"\"
""".strip()



def generate_gherkin_from_doc(doc_text, model="mistral:instruct", output_file="generated_tests.feature"):
    """Send the prompt to Ollama and save the generated Gherkin scenarios."""
    prompt = build_blackbox_prompt(doc_text)
    cmd = ["ollama", "run", model, prompt]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        stdout, stderr = process.communicate(timeout=120)

        if process.returncode != 0:
            print(f"Model error: {stderr}")
            return False

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(stdout)

        print(f"✅ Gherkin scenarios saved to {output_file}")
        return True

    except subprocess.TimeoutExpired:
        print("⏱️ Ollama model timed out.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    pdf_path = r"C:\Users\Selim\OneDrive\Bureau\ai test\docs\cahier.pdf"
    documentation_text = extract_text_from_pdf(pdf_path)

    if documentation_text.strip():
        print(f"📄 PDF text extracted. Length: {len(documentation_text)} characters.")
        success = generate_gherkin_from_doc(documentation_text)
        if not success:
            print("🔁 Trying fallback model: openhermes-2.5-mistral...")
            generate_gherkin_from_doc(documentation_text, model="openhermes-2.5-mistral")
    else:
        print("🚫 No documentation text extracted. Aborting.")
