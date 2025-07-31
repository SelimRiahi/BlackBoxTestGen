import json
import subprocess

def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def read_jsonl(file_path):
    objs = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    objs.append(json.loads(line.rstrip(', ')))
                except Exception:
                    pass
    return objs

def generate_steps_py_with_ollama(feature_text, scenario_log, num_tests, url):
    prompt = f'''
You are an expert Python QA automation engineer.

The web application under test is running at: {url}

You are given:
- The Gherkin feature file (test_scenarios_test.feature):
"""
{feature_text}
"""
- The scenario_actions_log.json file, which contains the actual UI actions and UI states observed during previous black-box Playwright runs.
{json.dumps(scenario_log)[:12000]}...  # Truncated for prompt size

IMPORTANT: When generating selectors for UI elements (inputs, buttons, etc.), you MUST use ONLY the names, labels, placeholders, ids, and button/link text that are present in the scenario_actions_log.json. NEVER invent, guess, or use any selector or element name that does not appear in the log. If you cannot find a matching selector in the log for a required action, SKIP that action and do not invent or guess any selector. Always prefer exact matches from the log for every action.

Your task:
1. For each scenario in the feature file, generate a full Python function named test_<scenario_name> (snake_case, no spaces or punctuation). Do NOT add a num_tests parameter to the functions.
2. For every scenario except registration and login, the function must first perform a login using username "samer" and password "123123" before executing the scenario steps.
3. Use the scenario_actions_log.json to infer the exact sequence of UI actions and all form fields, button clicks, and steps for each scenario. Do not use placeholders or comments like 'add fields', generate the full code for all actions and fields as observed in the log and feature file.
4. Each function should use Playwright Python syntax (async/await style) to perform the UI actions, filling forms, clicking buttons, etc., as inferred from the log and feature file.
5. For each scenario, generate exactly {num_tests} different sets of input data (e.g., usernames, task titles, etc.) and use them in the test logic. Always use the login credentials above for login.
6. At the end of the file, include a main function that runs all generated test functions sequentially using asyncio and Playwright, so the file can be run directly as a script. The main function should launch Playwright, call each test, and close Playwright. Use the standard Python __name__ == "__main__" idiom.
7. Output only valid Python code for the file steps_generated.py, with all imports, all scenario functions, and the main function as described. Output the code inside a single Python code block (start with ```python and end with ```). No explanations, only code.
'''
    result = subprocess.run(
        ["ollama", "run", "mistral"],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output = result.stdout.decode("utf-8")
    # Extract only the code between ```python and ```
    if '```python' in output:
        code = output.split('```python', 1)[1]
        code = code.split('```', 1)[0]
        return code.strip()
    # Fallback: Remove any code block markers if present
    if output.startswith("```"):
        output = output.split("```", 1)[1]
    return output.strip()

def main():
    feature_text = read_file("test_scenarios_test.feature")
    scenario_log = read_jsonl("scenario_actions_log.json")
    num_tests = 3  # Set the number of data variations to generate for each scenario
    url = "http://localhost:3001"
    steps_py = generate_steps_py_with_ollama(feature_text, scenario_log, num_tests, url)
    with open("steps_generated.py", "w", encoding="utf-8") as f:
        f.write(steps_py)
    print("steps_generated.py created successfully.")

if __name__ == "__main__":
    main()
