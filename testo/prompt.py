import subprocess
import json

def generate_scenario_prompt(ui_elements: list, api_traces: list) -> str:
    """
    Generates an optimized prompt for creating Gherkin scenarios
    and saves it to a file
    """
    # Strict prompt to force clean output
    phase1_prompt = f"""
    ROLE: You are a Gherkin Prompt Generator. Create STRICTLY a prompt for generating test scenarios.

    INPUT:
    UI Elements: {json.dumps(ui_elements, indent=2)}
    API Traces: {json.dumps(api_traces, indent=2)}

    RULES:
    1. OUTPUT ONLY THE PROMPT TEXT
    2. Format as markdown
    3. Structure for Gherkin scenario generation
    4. Include:
       - Clear instructions
       - Required scenario structure
       - Example format
    5. Never analyze the application
    6. Never include implementation code

    EXAMPLE OUTPUT:
    ```markdown
    Generate Gherkin scenarios using these rules:

    1. Create separate @ui and @api scenarios
    2. Use exact selectors from: [list selectors]
    3. Use exact API endpoints from: [list endpoints]
    4. Follow this structure:
    ```gherkin
    Feature: [Feature Name]
      @[tag]
      Scenario: [Description]
        Given [Context]
        When [Action]
        Then [Outcome]
    ```
    ```
    """

    # Execute Ollama Mistral
    cmd = ['ollama', 'run', 'mistral', phase1_prompt]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    stdout, _ = process.communicate()
    
    # Save to file
    with open('scenario_prompt.txt', 'w') as f:
        f.write(stdout.strip())
    
    return stdout.strip()

if __name__ == "__main__":
    # Load your data
    with open('ui_elements.json') as f:
        ui_data = json.load(f)
    
    with open('api_calls.json') as f:
        api_data = json.load(f)
    
    # Generate and save the prompt
    scenario_prompt = generate_scenario_prompt(ui_data, api_data)
    print("Scenario prompt generated and saved to scenario_prompt.txt")