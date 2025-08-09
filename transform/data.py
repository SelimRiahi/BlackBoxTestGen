import json
from pathlib import Path
import subprocess
import re

def load_json_file(file_path):
    """Load JSON data from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def save_enhanced_blueprint(data, output_path):
    """Save the enhanced blueprint to a file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved enhanced blueprint to {output_path}")
    except Exception as e:
        print(f"Error saving enhanced blueprint: {e}")

def query_llm(prompt):
    """Query the local LLM for element matching"""
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
    return stdout.strip()

def extract_json_from_response(response):
    """Robust JSON extraction that handles all response formats"""
    clean_response = response.strip()
    if clean_response.endswith('...'):
        clean_response = clean_response[:-3].strip()
    
    try:
        return json.loads(clean_response)
    except json.JSONDecodeError:
        pass
    
    json_match = re.search(r'```(?:json)?\n([\s\S]*?)\n```', clean_response)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    try:
        stack = []
        start_idx = -1
        for i, c in enumerate(clean_response):
            if c in ['{', '[']:
                if not stack:
                    start_idx = i
                stack.append(c)
            elif c in ['}', ']']:
                if stack:
                    stack.pop()
                if not stack and start_idx != -1:
                    return json.loads(clean_response[start_idx:i+1])
    except:
        pass
    
    return None

def handle_given_step(step_text, elements, api_calls):
    """Special handling for Given steps with URLs and authentication"""
    step_text = step_text.lower()
    result = []
    
    # First handle navigation URLs
    if 'navigate' in step_text or 'on the' in step_text:
        urls = set()
        
        # Get all unique URLs from API calls
        for call in api_calls:
            if 'url' in call:
                urls.add(call['url'])
        
        # Match the most relevant URL based on step text
        for url in urls:
            if 'login' in step_text and 'login' in url.lower():
                result.append({'url': url})
                break
            elif 'register' in step_text and 'register' in url.lower():
                result.append({'url': url})
                break
            elif 'task' in step_text and 'task' in url.lower():
                result.append({'url': url})
                break
    
    # Then add required elements for authentication if needed
    if 'logged in' in step_text or 'authenticated' in step_text:
        auth_elements = [
            e for e in elements 
            if any(field in e.get('id', '').lower() 
                  for field in ['username', 'password', 'login', 'auth'])
        ]
        result.extend(auth_elements)
    
    return result

def enhance_api_matching(step, api_calls):
    """Improved API call matching with strict requirements"""
    step_text = step['gherkin_text'].lower()
    matched_calls = []
    
    # Match by action type
    action_map = {
        'create': ['post'],
        'update': ['put', 'patch'],
        'delete': ['delete'],
        'check': ['get'],
        'status': ['get', 'patch'],
        'register': ['post'],
        'login': ['post']
    }
    
    # Find matching API calls based on step text and method
    for call in api_calls:
        # Skip calls without required fields
        if not all(k in call for k in ['url', 'method']):
            continue
            
        # Check for matching action verbs
        for action, methods in action_map.items():
            if action in step_text and call['method'].lower() in methods:
                matched_calls.append(call)
                break
    
    # If no matches found, fall back to URL matching
    if not matched_calls:
        keywords = ['task', 'login', 'register', 'status']
        for call in api_calls:
            if any(kw in call['url'].lower() for kw in keywords if kw in step_text):
                matched_calls.append(call)
    
    return matched_calls[:3]  # Return max 3 most relevant calls

def find_matching_elements(step, scenario, elements, api_calls, element_type):
    """Enhanced element matching with special handling for Given steps"""
    # Special handling for Given steps
    if step['gherkin_text'].strip().lower().startswith('given'):
        given_result = handle_given_step(step['gherkin_text'], elements, api_calls)
        if given_result:
            return given_result
    
    # Special handling for API steps
    if element_type == "API":
        return enhance_api_matching(step, api_calls)
    
    # Default LLM matching for other cases
    previous_steps = [s['gherkin_text'] for s in scenario['steps'] if s['step_id'] < step['step_id']]
    
    prompt = f"""TEST STEP ANALYSIS REQUIREMENTS:
1. For UI steps: Select ONLY the elements needed for THIS SPECIFIC ACTION
2. For API steps: Select ONLY the API calls relevant to THIS STEP
3. MUST maintain scenario flow consistency
4. Return ONLY a JSON array of matched elements

SCENARIO: {scenario['name']}
PREVIOUS STEPS: {previous_steps}
CURRENT STEP: {step['gherkin_text']}
STEP TYPE: {element_type}

AVAILABLE ELEMENTS:
{json.dumps(elements if element_type == "UI" else api_calls, indent=2)}

RETURN ONLY THE JSON ARRAY OF MATCHED ELEMENTS:"""

    response = query_llm(prompt)
    parsed_response = extract_json_from_response(response)
    
    if parsed_response is None:
        print(f"LLM failed to return valid JSON for step: {step['step_id']}")
        return []
    
    # Validate elements exist in original data
    valid_elements = []
    all_elements = elements if element_type == "UI" else api_calls
    element_ids = {e['id']: e for e in all_elements} if all_elements and 'id' in all_elements[0] else {}
    
    for item in parsed_response:
        if not isinstance(item, dict):
            continue
            
        # Match by ID if available
        if 'id' in item and item['id'] in element_ids:
            valid_elements.append(element_ids[item['id']])
            continue
            
        # Fallback to property matching
        for elem in all_elements:
            if all(str(elem.get(k)) == str(v) for k, v in item.items() if k in elem):
                valid_elements.append(elem)
                break
    
    return valid_elements

def enhance_blueprint(blueprint, ui_elements, api_calls):
    """Enhance the blueprint with matched elements"""
    for scenario in blueprint.get('scenarios', []):
        for step in scenario.get('steps', []):
            if step['type'] == 'UI':
                step['data'] = find_matching_elements(step, scenario, ui_elements, api_calls, "UI")
            elif step['type'] == 'API':
                step['data'] = find_matching_elements(step, scenario, ui_elements, api_calls, "API")
            else:
                step['data'] = []
    return blueprint

def main():
    # Define file paths
    base_dir = Path("C:/Users/Selim/OneDrive/Bureau/ai test")
    ui_path = base_dir / "testo/ui_elements.json"
    api_path = base_dir / "testo/api_calls.json"
    blueprint_path = base_dir / "transform/enhanced_blueprint.json"
    output_path = base_dir / "transform/enhanced_blueprint_final.json"
    
    # Load data files
    ui_elements = load_json_file(ui_path)
    api_calls = load_json_file(api_path)
    blueprint = load_json_file(blueprint_path)
    
    if None in [ui_elements, api_calls, blueprint]:
        print("Failed to load one or more input files")
        return
    
    # Enhance the blueprint
    enhanced_blueprint = enhance_blueprint(blueprint, ui_elements, api_calls)
    
    # Save the enhanced blueprint
    save_enhanced_blueprint(enhanced_blueprint, output_path)

if __name__ == "__main__":
    main()