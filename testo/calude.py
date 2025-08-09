import json
import subprocess

def generate_prompt_creator(ui_elements_json, api_endpoints_json):
    """
    Create a prompt that will generate another prompt for scenario creation
    """
    
    prompt_creator = f"""Analyze the provided UI elements and API endpoints data exactly as they are. Create a comprehensive prompt that will help another AI generate Gherkin test scenarios.

UI ELEMENTS DATA:
{json.dumps(ui_elements_json, indent=2)}

API ENDPOINTS DATA:
{json.dumps(api_endpoints_json, indent=2)}

YOUR TASK: Generate a detailed prompt that:

1. Describes what the application appears to do based STRICTLY on the data provided - no assumptions
2. Lists every UI element found and what it appears to do based on its tag, type, id, placeholder, text properties
3. Lists every API endpoint found with exact method, URL, and what data is sent/received
4. Only mentions functionality that is explicitly present in the data
5. Does not invent or assume any endpoints or features not shown

OUTPUT REQUIREMENTS:
Create a prompt that starts with: "You are an expert test scenario generator. Based on the application analysis below, create comprehensive Gherkin scenarios."

The prompt must include:
- Application analysis based only on what elements and endpoints exist
- Complete list of UI elements with their apparent functions
- Complete list of API endpoints with their exact methods and purposes
- Instructions to create scenarios that test every UI element and API endpoint found
- Request for comprehensive Gherkin scenarios covering all discovered functionality

Be precise - only analyze what is actually in the data. Do not add functionality that isn't there.

Generate the complete prompt now."""

    return prompt_creator

def run_prompt_generator(ui_file_path, api_file_path):
    """
    Load data and generate the final prompt using Ollama
    """
    
    # Load JSON files
    with open(ui_file_path, 'r') as f:
        ui_data = json.load(f)
    
    with open(api_file_path, 'r') as f:
        api_data = json.load(f)
    
    # Create the prompt that generates prompts
    prompt_creator = generate_prompt_creator(ui_data, api_data)
    
    # Run with Ollama to get the final prompt
    cmd = ['ollama', 'run', 'mistral', prompt_creator]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            generated_prompt = stdout.strip()
            
            # Save the generated prompt
            with open('final_prompt.txt', 'w') as f:
                f.write(generated_prompt)
            
            print("✅ Generated prompt saved to: final_prompt.txt")
            print("\n" + "="*60)
            print("GENERATED PROMPT:")
            print("="*60)
            print(generated_prompt)
            
            return generated_prompt
        else:
            print(f"❌ Error: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    generated_prompt = run_prompt_generator('ui_elements.json', 'api_calls.json')
    
    if generated_prompt:
        print(f"\n✅ Generated prompt ready for use with any AI model")
        print("📁 File: final_prompt.txt")