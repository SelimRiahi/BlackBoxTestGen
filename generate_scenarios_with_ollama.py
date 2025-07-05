import json
from PyPDF2 import PdfReader
import subprocess

def extract_text_from_pdf(pdf_path):
    # sourcery skip: inline-immediately-returned-variable, use-join
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def read_discovered_routes(routes_path):
    try:
        with open(routes_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def generate_scenarios_json_with_ollama(spec_text, feature_text, site_url, discovered_routes=None):
    routes_text = f"\nDiscovered routes in the app (from black-box Playwright exploration):\n{json.dumps(discovered_routes, indent=2)}\n" if discovered_routes else ""
    prompt = f'''
You are an expert test engineer AI.

The web application under test is running at: {site_url}
{routes_text}
Given the following system specification:
"""{spec_text}"""

And these Gherkin feature steps:
"""{feature_text}"""

Your task:
1) Extract and enhance test scenarios, mapping each Gherkin step to concrete test steps with input/output.
2) For every step, always provide a non-empty "input" (dict, even if just a url, form data, or action) and a non-empty "expected_output" (dict or string, e.g. page content, redirect, error message, etc). Use the discovered routes and site url to infer realistic inputs/outputs where possible.
3) Return the output as a JSON array of scenarios, each with:
   - "scenario_title"
   - "steps": list of steps with:
       - "keyword": "Given", "When", "Then"
       - "step_text": full Gherkin step text
       - "input": dict of inputs (never empty, always infer something)
       - "expected_output": dict or string explaining expected result (never empty)
4) No explanations, only JSON output.
5) Make output fully parsable JSON.

Output:
'''
    # Call ollama with the prompt
    result = subprocess.run(
        ["ollama", "run", "mistral", "--format", "json"],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output = result.stdout.decode("utf-8")
    # Try to parse JSON (strip code block if present)
    if output.startswith("```"):
        output = output.split("```", 1)[1]
    return json.loads(output)

def main():
    spec_text = extract_text_from_pdf("docs/cahier1.pdf")
    feature_text = read_file("test_scenarios.feature")
    site_url = "http://localhost:3001"
    discovered_routes = read_discovered_routes("discovered_routes.json")
    scenarios = generate_scenarios_json_with_ollama(spec_text, feature_text, site_url, discovered_routes)
    with open("generated_scenarios.json", "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2, ensure_ascii=False)
    print("generated_scenarios.json created successfully.")

if __name__ == "__main__":
    main()
