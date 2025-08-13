#!/usr/bin/env python3
import subprocess
import re
import json
import sys

def call_mistral(prompt, model="mistral"):
    """Call Ollama Mistral with the given prompt"""
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
        
        if process.returncode != 0:
            print(f"Error running Ollama: {stderr}")
            return None
            
        return stdout.strip()
        
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

def extract_scenarios_from_feature(feature_content):
    """Extract individual scenarios from Gherkin feature file"""
    scenarios = []
    current_scenario = None
    
    lines = feature_content.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('Scenario:'):
            if current_scenario:
                scenarios.append(current_scenario)
            current_scenario = {
                'name': line.replace('Scenario:', '').strip(),
                'steps': []
            }
        elif line and current_scenario and (line.startswith('Given') or line.startswith('When') or line.startswith('And') or line.startswith('Then')):
            current_scenario['steps'].append(line)
    
    if current_scenario:
        scenarios.append(current_scenario)
    
    return scenarios

def determine_page_context(scenario_name):
    """Determine the appropriate page context based on scenario name - generic for any web application"""
    scenario_lower = scenario_name.lower()
    
    # Map generic scenario keywords to generic page contexts
    if any(word in scenario_lower for word in ['login', 'log in', 'sign in', 'authentication']):
        return "Given I am on the login page"
    elif any(word in scenario_lower for word in ['register', 'registration', 'sign up', 'signup']):
        return "Given I am on the registration page"
    elif any(word in scenario_lower for word in ['logout', 'log out', 'sign out']):
        return "Given I am on the main page"
    elif any(word in scenario_lower for word in ['add', 'create', 'new']):
        return "Given I am on the creation page"
    elif any(word in scenario_lower for word in ['delete', 'remove']):
        return "Given I am on the management page"
    elif any(word in scenario_lower for word in ['form', 'validation', 'input']):
        return "Given I am on the form page"
    else:
        # Default fallback
        return "Given I am on the application page"

def transform_scenario(scenario):
    """Transform a single scenario using Mistral with enhanced Given step logic"""
    
    # Determine the appropriate page context
    given_step = determine_page_context(scenario['name'])
    
    # Create the transformation prompt for black-box testing
    prompt = f"""Transform this raw test scenario into generic, human-readable language suitable for black-box testing on any website. 

CRITICAL RULES - FOLLOW EXACTLY:
1. KEEP the scenario name EXACTLY as it is: "{scenario['name']}"
2. ONLY change "Given" steps that contain URLs/paths to: "{given_step}"
3. KEEP ALL OTHER STEPS EXACTLY THE SAME - do not change wording, do not add/remove steps
4. ONLY remove specific values from input fields (like "cvb" becomes empty), but keep the field names exactly
5. Do not change "When I enter", "And I click", "Then I should see" phrasing
6. Do not change any button names, field names, or element names
7. Do not change any error message descriptions
8. Keep the exact number of steps - do not combine or split steps

Original scenario:
Name: {scenario['name']}
Steps:
{chr(10).join(scenario['steps'])}

Transform ONLY by:
- Replace any "Given" step with URL/path with: "{given_step}"
- Remove specific input values but keep field names
- Keep everything else EXACTLY the same

Return format:
Scenario: {scenario['name']}
  {given_step}
  [keep other steps exactly as they are, just remove specific input values]

Only return the transformed scenario, nothing else."""

    result = call_mistral(prompt)
    if result:
        return result
    else:
        return f"Error transforming scenario: {scenario['name']}"

def process_feature_file(feature_content):
    """Process entire feature file and transform all scenarios"""
    scenarios = extract_scenarios_from_feature(feature_content)
    
    if not scenarios:
        print("No scenarios found in the feature file")
        return None
    
    print(f"Found {len(scenarios)} scenarios to transform...")
    
    transformed_scenarios = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"Transforming scenario {i}/{len(scenarios)}: {scenario['name']}")
        
        # Show which page context was determined
        page_context = determine_page_context(scenario['name'])
        print(f"  → Using: {page_context}")
        
        transformed = transform_scenario(scenario)
        if transformed:
            transformed_scenarios.append(transformed)
        else:
            print(f"Failed to transform scenario: {scenario['name']}")
    
    return transformed_scenarios

def create_generic_feature_file(transformed_scenarios):
    """Create a new feature file with transformed scenarios"""
    
    feature_header = """Feature: Generic Application Test Scenarios
  As a user testing any web application
  I want to perform various user interactions
  So that I can verify the application responds correctly to both valid and invalid inputs

"""
    
    full_content = feature_header + "\n\n".join(transformed_scenarios)
    return full_content

def main():
    """Main function"""
    
    # Default path to the feature file
    default_feature_file = r"C:\Users\Selim\Downloads\recorded-enhanced (1).feature"
    
    # Check if user provided a different path
    if len(sys.argv) > 1:
        feature_file = sys.argv[1]
    else:
        feature_file = default_feature_file
    
    # Read feature file content
    try:
        with open(feature_file, 'r', encoding='utf-8') as f:
            feature_content = f.read()
        print(f"✅ Successfully loaded feature file: {feature_file}")
    except FileNotFoundError:
        print(f"❌ Feature file not found: {feature_file}")
        print("Please make sure the file exists or provide the correct path as an argument.")
        return
    except Exception as e:
        print(f"❌ Error reading feature file: {e}")
        return

    print("Starting black-box scenario transformation...")
    print("🔄 Converting technical scenarios to generic user flows...")
    print("=" * 60)
    
    # Process the feature file
    transformed_scenarios = process_feature_file(feature_content)
    
    if not transformed_scenarios:
        print("❌ No scenarios were successfully transformed")
        return
    
    print("=" * 60)
    print("📝 Creating generic feature file...")
    
    # Create the final feature file
    generic_feature = create_generic_feature_file(transformed_scenarios)
    
    # Save to file in the same directory as the input file
    import os
    input_dir = os.path.dirname(feature_file) if os.path.dirname(feature_file) else "."
    output_filename = os.path.join(input_dir, "generic_blackbox_scenarios.feature")
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(generic_feature)
        print(f"✅ Generic black-box scenarios saved to: {output_filename}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        
    # Also print to console
    print("\n" + "=" * 60)
    print("🎯 TRANSFORMED BLACK-BOX SCENARIOS:")
    print("=" * 60)
    print(generic_feature)
    
    print("\n" + "=" * 60)
    print("ℹ️  These scenarios can now be used to test any web application!")
    print("   They focus on user actions without assuming specific functionality.")
    print("   Given steps are now contextually appropriate based on scenario names.")

if __name__ == "__main__":
    main()