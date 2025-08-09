import subprocess
import json
from pathlib import Path

def build_blackbox_prompt(doc_text):
    """Create a strictly generic blackbox testing prompt"""
    return f"""
Generate comprehensive Gherkin test scenarios from the provided application data following these strict rules:

1. Structure scenarios in this exact order:
   - User Registration (success + failure cases)
   - User Authentication (success + failure cases)
   - CRUD Operations (success + failure cases)
   - UI State Validation

2. Use ONLY these generic terms:
   - "resource" instead of domain-specific terms
   - "credentials" instead of username/password
   - "UI element" instead of specific component names
   - "endpoint" for API routes

3. For each operation include:
   - 1 success scenario
   - 1-2 common failure scenarios
   - Parameterized values where appropriate (use {{VALUE}} notation)

4. Follow this exact scenario template:
# Feature: [Functional Area]
Scenario: [Specific interaction]
  Given [Initial context]
  When [Action performed]
  Then [Expected outcome]

5. Never test individual UI component clicks (like buttons)
6. Only create scenarios for complete user flows
7. Include UI state validations where appropriate
8. Make all scenarios completely application-agnostic

Application Data:
{doc_text}

Generate scenarios covering all observed:
- Registration flows
- Authentication flows
- CRUD operations
- UI state changes
- API interactions
"""

def generate_gherkin_from_doc(doc_text, model="mistral", output_file="generated_tests.feature"):
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
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            with open(output_file, "w") as f:
                f.write(stdout)
            print(f"Success! Scenarios saved to {output_file}")
            return True
        else:
            print(f"Error generating scenarios:\n{stderr}")
            return False
            
    except Exception as e:
        print(f"Execution failed: {e}")
        return False

def load_and_generate(input_file="test_data.json"):
    """Load JSON data and generate tests with strict data mapping"""
    try:
        with open(input_file) as f:
            data = json.load(f)
        
        # Create completely generic data summary
        summary = {
            "authentication_flows": {
                "components": list(set(
                    el["id"].split('-')[0] 
                    for el in data.get("uiElements", [])
                    if any(kw in el["id"] for kw in ["auth", "login", "register"])
                )),
                "endpoints": list(set(
                    f"{call['method']} {call['url'].split('?')[0].split('/')[-1]}"
                    for call in data.get("apiCalls", [])
                    if any(kw in call["url"] for kw in ["auth", "login", "register"])
                ))
            },
            "crud_operations": {
                "components": list(set(
                    el["id"].split('-')[0] + ("-{{ID}}" if "dynamicProperties" in el else "")
                    for el in data.get("uiElements", [])
                    if not any(kw in el["id"] for kw in ["auth", "login", "register"])
                )),
                "endpoints": list(set(
                    f"{call['method']} {call['url'].split('?')[0].split('/')[-2] if len(call['url'].split('/')) > 1 else 'root'}"
                    for call in data.get("apiCalls", [])
                    if not any(kw in call["url"] for kw in ["auth", "login", "register"])
                ))
            },
            "ui_states": list(set(
                state["action"].replace("API_CALL_", "")
                for state in data.get("uiStateHistory", [])
            ))
        }
        
        generate_gherkin_from_doc(json.dumps(summary, indent=2))
        
    except Exception as e:
        print(f"Error loading data: {e}")

if __name__ == "__main__":
    load_and_generate()