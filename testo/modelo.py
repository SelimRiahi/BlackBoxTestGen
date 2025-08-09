import json
import subprocess
import re

# Load the test blueprint JSON file
with open('enhanced_blueprint.json', 'r', encoding='utf-8') as f:
    blueprint_data = json.load(f)

# Build prompt with updated instructions
prompt = """
You are a Python test generator.

You will be given a JSON array of test scenarios. Each scenario includes:
- `title`: the name of the test
- `steps`: a sequence of test actions

Each step contains:
- `type`: one of ["navigate", "input", "click", "assert"]
- `target`: a DOM selector or URL path
- `value`: used for input or expected status

## Your task:
Generate a valid Python test file using Playwright and Pytest.

### Guidelines:
- One test function per scenario
- Use `async def` and `@pytest.mark.asyncio`
- Use `async_playwright()` to create Playwright instance
- Use `browser.new_page()` (not `newPage()`)
- Do not use `Playwright.create()` — it doesn't exist
- Use only valid Playwright Python API
- Each function must be named based on its `title`, converted to snake_case
- Use only exact values from the JSON (black-box test)
- DO NOT invent selectors, test data, or logic
- Do NOT reference `response_status` unless it's explicitly in the DOM
- Do NOT add comments, markdown, or explanation text
- Output pure Python code — no ``` fences, no extra headers

### Step Type to Code Mapping:

| type     | Code                                 |
|----------|--------------------------------------|
| navigate | await page.goto("URL")               |
| input    | await page.fill("SELECTOR", "VALUE") |
| click    | await page.click("SELECTOR")         |
| assert   | assert True  # expected: VALUE       |

Now generate test functions using this blueprint:
"""

# Append formatted blueprint JSON to prompt
prompt += "\n" + json.dumps(blueprint_data, indent=2)

# Run prompt with Ollama and Mistral
cmd = ['ollama', 'run', 'mistral', prompt]
process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding='utf-8',
    errors='replace'
)
stdout, stderr = process.communicate()


def clean_code_output(output: str) -> str:
    lines = output.splitlines()

    # Remove any lines before the real code starts (imports or pytest defs)
    for i, line in enumerate(lines):
        if re.match(r"^\s*(import|from|@pytest|async def|def)\b", line):
            lines = lines[i:]
            break

    # Remove markdown code fences and unwanted headers
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped in ("```", "```python"):
            continue
        if any(stripped.startswith(prefix) for prefix in [
            "Here is the", "Here’s the", "Based on your", "Below is the"
        ]):
            continue
        cleaned_lines.append(line)

    # Trim trailing empty lines
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()

    return "\n".join(cleaned_lines).strip() + "\n"


# Clean up LLM output
cleaned_code = clean_code_output(stdout)

# Write cleaned code to file
output_file = 'generated_tests.py'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(cleaned_code)

print(f"[✔] Tests generated and saved to: {output_file}")
if stderr:
    print(f"[!] stderr:\n{stderr}")
