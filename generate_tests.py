import ollama
import os

def load_docs():
    """Load documentation files without any interpretation"""
    with open("docs/api_docs.txt", "r", encoding='utf-8') as f:
        api_docs = f.read()
    with open("docs/requirements.txt", "r", encoding='utf-8') as f:
        requirements = f.read()
    return api_docs, requirements

def generate_prompt(test_type, base_url, api_docs, requirements):
    """Create prompt without any problematic string formatting"""
    lang = "javascript" if test_type == "frontend" else "python"
    imports = 'const { test, expect } = require("@playwright/test")' if test_type == "frontend" else 'import pytest\nimport requests'
    
    return f"""STRICT BLACKBOX TEST GENERATION:
Create {test_type} tests using ONLY the documented behavior.
Treat the system as a complete black box - no internal knowledge.

DOCUMENTATION:
{api_docs}

REQUIREMENTS:
{requirements}

INSTRUCTIONS:
1. Use BASE_URL = "{base_url}"
2. Only test documented behavior
3. No assumptions about implementation
4. Each test must be completely independent
5. Include both success and error cases

OUTPUT FORMAT:
```{lang}
{imports}

BASE_URL = "{base_url}"

/* Independent test cases */
```"""

def generate_tests(test_type):
    """Generate blackbox tests for specified type"""
    api_docs, requirements = load_docs()
    base_url = "http://localhost:3000" if test_type == "backend" else "http://localhost:3001"
    
    prompt = generate_prompt(test_type, base_url, api_docs, requirements)
    
    response = ollama.generate(
        model="mistral",
        prompt=prompt,
        options={'temperature': 0.2, 'num_ctx': 8000}
    )
    
    try:
        # Extract code block between triple backticks
        parts = response['response'].split("```")
        if len(parts) > 1:
            code = parts[1].split("\n", 1)[1].strip()  # Remove language specifier
        else:
            raise ValueError("No code block found")
    except Exception:
        code = generate_fallback_test(test_type, base_url)
    
    save_test_file(test_type, code)

def generate_fallback_test(test_type, base_url):
    """Minimal fallback tests"""
    if test_type == "backend":
        return f"""import pytest
import requests

BASE_URL = "{base_url}"

def test_service_available():
    response = requests.get(f"{base_url}/")
    assert response.status_code != 404
"""
    else:
        return f"""const {{ test, expect }} = require('@playwright/test');

BASE_URL = "{base_url}";

test('Page loads', async ({{ page }}) => {{
  await page.goto('{base_url}');
  await expect(page).not.toHaveTitle('404');
}});
"""

def save_test_file(test_type, content):
    """Save test file with proper encoding"""
    os.makedirs("generated_tests", exist_ok=True)
    ext = "js" if test_type == "frontend" else "py"
    filename = f"test_{test_type}.{ext}"
    with open(f"generated_tests/{filename}", "w", encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {filename}")

if __name__ == "__main__":
    generate_tests("backend")
    generate_tests("frontend")