import subprocess
import re
import json
from textwrap import dedent
from PyPDF2 import PdfReader

def extract_pdf_text(pdf_path):  # sourcery skip: use-join
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def load_feature_file(feature_path):
    with open(feature_path, "r", encoding="utf-8") as f:
        return f.read()

def call_ai_model(prompt, model_name="mistral"):
    cmd = ['ollama', 'run', model_name, prompt]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    stdout, stderr = process.communicate(timeout=300)
    if process.returncode != 0:
        raise RuntimeError(f"AI call failed: {stderr}")
    return stdout.strip()

def build_prompt(spec_text, feature_text):
    # sourcery skip: inline-immediately-returned-variable
    prompt = dedent(f"""
    You are an expert test engineer AI.

    Given the following system specification:
    \"\"\"{spec_text}\"\"\"

    And these Gherkin feature steps:
    \"\"\"{feature_text}\"\"\"

    Your task:
    1) Extract and enhance test scenarios, mapping each Gherkin step to concrete test steps with input/output.
    2) Return the output as a JSON array of scenarios, each with:
       - "scenario_title"
       - "steps": list of steps with:
           - "keyword": "Given", "When", "Then"
           - "step_text": full Gherkin step text
           - "input": dict of inputs if applicable (e.g. url, method, payload)
           - "expected_output": dict or string explaining expected result
    3) No explanations, only JSON output.
    4) Make output fully parsable JSON.

    Output:
    """)
    return prompt

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_behave_steps_from_json(scenarios):
    # sourcery skip: low-code-quality
    step_impls = []
    imports = "from behave import given, when, then\nimport requests\n\n"

    implemented_steps = set()

    for scenario in scenarios:
        for step in scenario.get("steps", []):
            keyword = step.get("keyword", "").lower()
            step_text = step.get("step_text", "")
            input_data = step.get("input", {})
            expected_output = step.get("expected_output", "")

            if step_text in implemented_steps:
                continue
            implemented_steps.add(step_text)

            func_name = re.sub(r'\W+', '_', step_text.lower()).strip('_')

            decorator = {
                "given": "@given",
                "when": "@when",
                "then": "@then"
            }.get(keyword, "@when")

            code = f'{decorator}("{step_text}")\ndef step_impl_{func_name}(context):\n'

            url = input_data.get("url")
            method = input_data.get("method", "get").lower()
            payload = input_data.get("payload", None)
            response_payload = input_data.get("responsePayload", None)

            if url:
                if method in ["post", "put", "patch"]:
                    code += f"    response = requests.{method}('{url}', json={payload or {{}}})\n"
                else:
                    code += f"    response = requests.{method}('{url}')\n"
                code += "    context.response = response\n"
                code += "    assert 200 <= response.status_code < 300, f\"Unexpected status code: {response.status_code}\"\n"
                if response_payload:
                    # Add checks for response keys/values
                    for key, val in response_payload.items():
                        code += f"    assert response.json().get('{key}') == {json.dumps(val)}, \"Expected {key} in response\"\n"
            else:
                code += "    pass  # TODO: Implement step logic\n"

            if isinstance(expected_output, str) and expected_output.strip():
                expected_escaped = expected_output.replace("\"", "\\\"")
                code += f"    # Expected: {expected_escaped}\n"

            code += "\n"
            step_impls.append(code)

    return imports + "\n".join(step_impls)

def main():
    print("📄 Extracting system specification text from PDF...")
    spec_text = extract_pdf_text("docs/cahier1.pdf")

    print("📄 Loading Gherkin feature file...")
    feature_text = load_feature_file("test_scenarios.feature")

    print("🤖 Building prompt for AI...")
    prompt = build_prompt(spec_text, feature_text)

    print("🧠 Sending prompt to AI model...")
    ai_response = call_ai_model(prompt)

    print("🧾 Parsing AI response JSON...")
    try:
        scenarios = json.loads(ai_response)
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON from AI response. Raw output:")
        print(ai_response)
        return

    print(f"✅ Parsed {len(scenarios)} scenarios.")

    save_json(scenarios, "generated_scenarios1.json")
    print("💾 Saved scenarios JSON to generated_scenarios.json")

    print("⚙️ Generating Behave step implementations from JSON...")
    behave_code = generate_behave_steps_from_json(scenarios)

    with open("steps_generated.py", "w", encoding="utf-8") as f:
        f.write(behave_code)

    print("💾 Generated Behave step implementation file steps_generated.py")

if __name__ == "__main__":
    main()
