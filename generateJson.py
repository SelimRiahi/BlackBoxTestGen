import subprocess
import re
import json
from textwrap import dedent

def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_feature_file(feature_path):
    with open(feature_path, "r", encoding="utf-8") as f:
        return f.read()

def call_ai_model(prompt, model_name="llama3.1"):
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
    prompt = dedent(f"""
You are an expert test engineer AI working with a RESTful API backend and front-end UI.

You have the following UI discovery data extracted from the application:
\"\"\"{spec_text}\"\"\"

You also have these limited Gherkin feature steps:
\"\"\"{feature_text}\"\"\"

Your goal is to generate a comprehensive JSON array of test scenarios based on both the UI structure and the feature steps.

Guidelines:
- Use the UI discovery data to understand the UI elements, forms, and fields available.
- Use the provided feature steps as a starting point, but you may extrapolate additional relevant test scenarios.
- Each scenario must include a "scenario_title" and a list of "steps".
- "Given" steps represent preconditions and should NOT include API calls unless explicitly stated.
- "When" steps represent user actions or API calls, and must have an "input" object with:
    - "method": HTTP method (POST, GET, etc.)
    - "endpoint": API endpoint path (e.g., "/example_endpoint")
    - optionally "body" with JSON payload using generic placeholders like "field1", "field2"
- "Then" and "And" steps represent expected outcomes and must have an "expected_output" object with:
    - "statusCode": HTTP status code integer
    - "jsonResponse": JSON object with expected response keys and generic string values
- Avoid using real usernames, emails, or domain-specific data; use generic placeholders only.
- Generate tests that cover typical and edge cases relevant to the discovered UI elements.
- Output a single valid JSON array only; do not include explanations, markdown, or extra text.
- **Give actual example inputs, and make sure to repeat input fields when necessary**

Example output:

[
  {{
    "scenario_title": "Successful operation with valid input",
    "steps": [
      {{
        "keyword": "Given",
        "step_text": "the user is on the relevant page"
      }},
      {{
        "keyword": "When",
        "step_text": "the user submits the form with required fields",
        "input": {{
          "method": "POST",
          "endpoint": "/example_endpoint",
          "body": {{
            "field1": "example",
            "field2": "example"
          }}
        }}
      }},
      {{
        "keyword": "Then",
        "step_text": "a success message is displayed and a token is returned",
        "expected_output": {{
          "statusCode": 201,
          "jsonResponse": {{
            "message": "Operation successful",
            
          }}
        }}
      }}
    ]
  }}
]


Output:
""")
    return prompt

def clean_ai_output(output):
    # Find the first { or [ character that might indicate start of JSON
    json_start = re.search(r'[\[\{]', output)
    if not json_start:
        return output.strip()

    json_str = output[json_start.start():].strip()

    # Remove common markdown fences
    json_str = re.sub(r'^```json\s*', '', json_str)
    json_str = re.sub(r'^```\s*', '', json_str)
    json_str = re.sub(r'```$', '', json_str.strip())

    # Try parsing smaller substrings to get valid JSON
    for end_index in range(len(json_str), len(json_str) - 2000, -1):
        candidate = json_str[:end_index]
        try:
            json.loads(candidate)
            return candidate.strip()
        except json.JSONDecodeError:
            continue

    return json_str.strip()

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_behave_steps_from_json(scenarios, base_url="http://localhost:3001"):
    step_impls = []
    imports = (
        "from behave import given, when, then\n"
        "import requests\n"
        "import json\n\n"
    )

    implemented_steps = set()
    last_keyword = None

    for scenario in scenarios:
        for step in scenario.get("steps", []):
            keyword_raw = step.get("keyword", "").lower()
            keyword = last_keyword if keyword_raw == "and" else keyword_raw
            last_keyword = keyword

            step_text = step.get("step_text", "")
            input_data = step.get("input")
            expected_output = step.get("expected_output")

            if step_text in implemented_steps:
                continue
            implemented_steps.add(step_text)

            step_text_escaped = step_text.replace('"', '\\"')
            decorator = {
                "given": "@given",
                "when": "@when",
                "then": "@then"
            }.get(keyword, "@when")

            func_name = re.sub(r'\W+', '_', step_text.lower()).strip('_')
            func_name = re.sub(r'\d+', 'num', func_name)
            if func_name and func_name[0].isdigit():
                func_name = '_' + func_name

            code = f'{decorator}("{step_text_escaped}")\ndef step_impl_{func_name}(context):\n'

            if input_data and "endpoint" in input_data:
                method = input_data.get("method", "get").lower()
                endpoint = input_data.get("endpoint")
                if not endpoint.startswith("http"):
                    endpoint = base_url.rstrip("/") + "/" + endpoint.lstrip("/")

                payload_raw = input_data.get("body")
                payload = None
                if payload_raw:
                    try:
                        if isinstance(payload_raw, str):
                            payload = json.loads(payload_raw)
                        else:
                            payload = payload_raw
                    except Exception:
                        payload = None

                if method in ["post", "put", "patch"]:
                    if payload:
                        code += f"    response = requests.{method}('{endpoint}', json={json.dumps(payload)})\n"
                    else:
                        code += f"    response = requests.{method}('{endpoint}')\n"
                else:
                    code += f"    response = requests.{method}('{endpoint}')\n"

                code += "    context.response = response\n"

            elif keyword == "then" and expected_output:
                code += "    response = context.response\n"

                status_code = expected_output.get("statusCode")
                json_resp = expected_output.get("jsonResponse")

                if status_code is not None:
                    code += f"    assert response.status_code == {status_code}, f'Expected status code {status_code} but got {{response.status_code}}'\n"

                if isinstance(json_resp, dict):
                    def gen_json_assertions(d, parent="response.json()"):
                        assertions = ""
                        for k, v in d.items():
                            if isinstance(v, dict):
                                assertions += gen_json_assertions(v, parent + f".get('{k}', {{}})")
                            elif isinstance(v, list):
                                assertions += f"    assert '{k}' in {parent}, 'Expected key \"{k}\" in response JSON'\n"
                                assertions += f"    assert isinstance({parent}['{k}'], list), 'Expected \"{k}\" to be a list'\n"
                            elif isinstance(v, str) and v.lower() in ["jsonwebtoken", "token", "somevalue", "string"]:
                                assertions += f"    assert '{k}' in {parent}, 'Expected key \"{k}\" in response JSON'\n"
                            else:
                                assertions += f"    assert {parent}.get('{k}') == {json.dumps(v)}, 'Expected {k} to be {json.dumps(v)}'\n"
                        return assertions
                    code += gen_json_assertions(json_resp)

                code += "\n"

            else:
                code += "    pass\n\n"

            step_impls.append(code)

    return imports + "\n".join(step_impls)

def main():
    print("📄 Loading ui discovery  from ui-extracted.json...")
    spec_data = load_json_file("ui-extracted.json")

    # Convert JSON data to string for prompt, limit length
    spec_text = json.dumps(spec_data)[:3000]

    print("📄 Loading Gherkin feature file...")
    feature_text = load_feature_file("features/test_scenarios.feature")

    print("🤖 Building prompt for AI...")
    prompt = build_prompt(spec_text, feature_text)

    print("🧠 Sending prompt to AI model...")
    ai_response = call_ai_model(prompt)

    print("🧾 Cleaning AI output...")
    ai_response = clean_ai_output(ai_response)

    print("🧾 Parsing AI response JSON...")
    try:
        scenarios = json.loads(ai_response)
    except json.JSONDecodeError as e:
        print("❌ Failed to parse JSON from AI response.")
        print("Error:", e)
        print("Raw output:")
        print(ai_response)
        return

    print(f"✅ Parsed {len(scenarios)} scenarios.")

    save_json(scenarios, "generated_scenarios.json")
    print("💾 Saved scenarios JSON to generated_scenarios.json")

    print("⚙️ Generating Behave step implementations from JSON...")
    behave_code = generate_behave_steps_from_json(scenarios)

    with open("features/steps/steps_generated.py", "w", encoding="utf-8") as f:
        f.write(behave_code)

    print("💾 Generated Behave step implementation file steps_generated.py")

if __name__ == "__main__":
    main()
