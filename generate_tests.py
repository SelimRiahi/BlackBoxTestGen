import ollama
import os

def load_docs():
    """Load raw documents without interpretation"""
    with open("docs/api_docs.txt", "r") as f:
        api_docs = f.read()
    with open("docs/requirements.txt", "r") as f:
        requirements = f.read()
    return api_docs, requirements

def generate_tests():
    api_docs, requirements = load_docs()
    
    prompt = f"""
    STRICT BLACKBOX TEST GENERATION:
    Create pytest tests using ONLY these documents.
    NEVER assume technologies or internals.
    
    API DOCS:
    {api_docs}
    
    REQUIREMENTS:
    {requirements}
    
    RULES:
    1. Test ONLY documented behavior
    2. Use only:
       - HTTP status codes
       - Response field checks
       - Performance requirements
    3. Output format:
    ```python
    import pytest
    import requests
    
    BASE_URL = "{{config}}"
    
    # Tests here
    ```
    """
    
    response = ollama.generate(
        model="mistral",
        prompt=prompt,
        options={
            'temperature': 0.3,
            'num_ctx': 4000
        }
    )
    
    # Extract code between ```python ```
    code = response['response'].split("```python")[1].split("```")[0].strip()
    
    os.makedirs("generated_tests", exist_ok=True)
    with open("generated_tests/test_api.py", "w") as f:
        f.write(code)

if __name__ == "__main__":
    generate_tests()