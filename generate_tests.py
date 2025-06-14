import ollama
import os
import re

def load_docs():
    """Load raw documents without interpretation"""
    with open("docs/api_docs.txt", "r") as f:
        api_docs = f.read()
    with open("docs/requirements.txt", "r") as f:
        requirements = f.read()
    return api_docs, requirements

def generate_tests():
    api_docs, requirements = load_docs()
    
    # Auto-detect port from docs
    port_match = re.search(r"Default Port: (\d+)", api_docs)
    port = port_match.group(1) if port_match else "3000"
    base_url = f"http://localhost:{port}"
    
    prompt = f"""
    STRICT BLACKBOX TEST GENERATION:
    Create direct API tests using ONLY the documented behavior.
    
    API DOCS:
    {api_docs}
    
    REQUIREMENTS:
    {requirements}
    
    INSTRUCTIONS:
    1. Use BASE_URL = "{base_url}" (detected from docs)
    2. Test only documented endpoints and responses
    3. Keep tests simple - no mocks or fixtures
    4. Include happy path and error cases
    5. Add clear docstrings explaining each test
    
    OUTPUT FORMAT:
    ```python
    import pytest
    import requests
    
    BASE_URL = "{base_url}"
    
    # Test cases...
    ```
    """
    
    response = ollama.generate(
        model="mistral",
        prompt=prompt,
        options={
            'temperature': 0.2,  # More deterministic
            'num_ctx': 8000
        }
    )
    
    # Clean extraction
    try:
        code = response['response'].split("```python")[1].split("```")[0].strip()
        # Ensure BASE_URL matches our detection
        code = code.replace('BASE_URL = "{{config}}"', f'BASE_URL = "{base_url}"')
    except IndexError:
        code = f"""import pytest
import requests

BASE_URL = "{base_url}"

# Failed to generate tests - using minimal template
def test_api_available():
    response = requests.get(f"{{BASE_URL}}/tasks")
    assert response.status_code in [200, 401]  # Either OK or requires auth
"""
    
    os.makedirs("generated_tests", exist_ok=True)
    with open("generated_tests/test_api.py", "w") as f:
        f.write(code)

if __name__ == "__main__":
    generate_tests()