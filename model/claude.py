import json
import subprocess
import re

def parse_gherkin_scenarios(feature_content):
    """
    Parse Gherkin scenarios into structured format
    """
    scenarios = []
    lines = feature_content.split('\n')
    current_scenario = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('Scenario:'):
            if current_scenario:
                scenarios.append(current_scenario)
            current_scenario = {
                'name': line.replace('Scenario:', '').strip(),
                'steps': []
            }
        elif line.startswith(('Given ', 'When ', 'Then ', 'And ')):
            if current_scenario:
                step_type = line.split()[0]
                step_text = line[len(step_type):].strip()
                current_scenario['steps'].append({
                    'type': step_type,
                    'text': step_text
                })
    
    if current_scenario:
        scenarios.append(current_scenario)
    
    return scenarios

def find_matching_ui_element(step_text, ui_elements):
    """
    Find UI elements that might match this step based on keywords
    """
    step_lower = step_text.lower()
    
    # Generic keywords that could appear in any application
    action_keywords = {
        'click': ['button', 'link', 'submit'],
        'type': ['input', 'text', 'field'],
        'select': ['select', 'dropdown', 'option'],
        'check': ['checkbox', 'check'],
        'navigate': ['nav', 'menu', 'link'],
        'fill': ['input', 'text', 'field', 'form'],
        'enter': ['input', 'text', 'field'],
        'choose': ['select', 'dropdown', 'radio'],
        'provide': ['input', 'text', 'field'],
        'submit': ['submit', 'button', 'form']
    }
    
    matches = []
    for element in ui_elements:
        element_data = str(element).lower()
        
        score = 0
        # Check if step contains action words and element contains matching types
        for action, element_types in action_keywords.items():
            if action in step_lower:
                for elem_type in element_types:
                    if elem_type in element_data:
                        score += 5
        
        # Check for direct text matches in element properties
        element_text = (str(element.get('text', '')) + ' ' + 
                       str(element.get('placeholder', '')) + ' ' + 
                       str(element.get('id', '')) + ' ' + 
                       str(element.get('selector', ''))).lower()
        
        # Split step into words and check for matches
        step_words = re.findall(r'\b\w+\b', step_lower)
        for word in step_words:
            if len(word) > 2 and word in element_text:  # Ignore short words
                score += 3
        
        if score > 0:
            matches.append((element, score))
    
    # Return all matches sorted by score
    return sorted(matches, key=lambda x: x[1], reverse=True)

def find_matching_api_endpoint(step_text, api_endpoints):
    """
    Find API endpoints that might be relevant for this step
    """
    step_lower = step_text.lower()
    
    # Generic HTTP action mapping
    http_actions = {
        'create': ['post'],
        'add': ['post'],
        'submit': ['post'],
        'register': ['post'],
        'login': ['post'],
        'update': ['put', 'patch'],
        'modify': ['put', 'patch'],
        'change': ['put', 'patch'],
        'delete': ['delete'],
        'remove': ['delete'],
        'get': ['get'],
        'fetch': ['get'],
        'retrieve': ['get'],
        'view': ['get'],
        'logout': ['post', 'delete']
    }
    
    matches = []
    for endpoint in api_endpoints:
        endpoint_data = str(endpoint).lower()
        method = str(endpoint.get('method', '')).lower()
        url = str(endpoint.get('url', '')).lower()
        
        score = 0
        
        # Check if step action matches HTTP method
        for action, methods in http_actions.items():
            if action in step_lower and method in methods:
                score += 10
        
        # Check for URL path matches with step words
        step_words = re.findall(r'\b\w+\b', step_lower)
        for word in step_words:
            if len(word) > 2 and word in url:
                score += 5
        
        if score > 0:
            matches.append((endpoint, score))
    
    return sorted(matches, key=lambda x: x[1], reverse=True)

def generate_step_mapping(scenarios, ui_elements, api_endpoints):
    """
    Generate mapping for each step in each scenario
    """
    mappings = []
    
    for scenario in scenarios:
        scenario_mapping = {
            'scenario_name': scenario['name'],
            'steps': []
        }
        
        for step in scenario['steps']:
            step_mapping = {
                'step_type': step['type'],
                'step_text': step['text'],
                'ui_elements': [],
                'api_endpoints': [],
                'actions': []
            }
            
            # Find matching UI elements
            ui_matches = find_matching_ui_element(step['text'], ui_elements)
            step_mapping['ui_elements'] = ui_matches[:3]  # Top 3 matches
            
            # Find matching API endpoints
            api_matches = find_matching_api_endpoint(step['text'], api_endpoints)
            step_mapping['api_endpoints'] = api_matches[:2]  # Top 2 matches
            
            # Determine actions based on step type and content
            step_mapping['actions'] = determine_actions(step)
            
            scenario_mapping['steps'].append(step_mapping)
        
        mappings.append(scenario_mapping)
    
    return mappings

def determine_actions(step):
    """
    Determine what actions should be taken for this step
    """
    step_lower = step['text'].lower()
    step_type = step['type'].lower()
    
    actions = []
    
    if step_type == 'given':
        if 'navigate' in step_lower or 'page' in step_lower:
            actions.append('navigate')
        elif 'logged' in step_lower or 'authenticated' in step_lower:
            actions.append('authenticate')
        else:
            actions.append('setup')
    
    elif step_type == 'when':
        if any(word in step_lower for word in ['click', 'press', 'submit']):
            actions.append('click')
        elif any(word in step_lower for word in ['type', 'enter', 'provide', 'fill']):
            actions.append('input')
        elif any(word in step_lower for word in ['select', 'choose']):
            actions.append('select')
        elif 'navigate' in step_lower:
            actions.append('navigate')
        else:
            actions.append('interact')
    
    elif step_type == 'then':
        if any(word in step_lower for word in ['see', 'display', 'show', 'appear']):
            actions.append('verify_display')
        elif any(word in step_lower for word in ['message', 'error', 'success']):
            actions.append('verify_message')
        elif 'redirect' in step_lower or 'navigate' in step_lower:
            actions.append('verify_navigation')
        else:
            actions.append('verify')
    
    return actions

def create_llm_enhanced_prompt(ui_elements_json, api_endpoints_json, feature_file_content):
    """
    Create a prompt that uses LLM to intelligently map each step with complete coverage
    """
    
    # Parse scenarios to count them
    scenarios = parse_gherkin_scenarios(feature_file_content)
    total_scenarios = len(scenarios)
    total_steps = sum(len(scenario['steps']) for scenario in scenarios)
    
    prompt = f"""You are an expert test automation engineer. Create COMPLETE step-by-step mapping for ALL {total_scenarios} scenarios with ALL {total_steps} steps.

## CRITICAL SUCCESS CRITERIA:
✅ Must map ALL {total_scenarios} scenarios - zero missing
✅ Must map ALL {total_steps} steps - zero missing  
✅ Every GIVEN step must specify URL location
✅ Use only provided elements with exact selectors

## AVAILABLE UI ELEMENTS (USE ONLY THESE):
"""
    
    # List all UI elements with exact data
    for i, element in enumerate(ui_elements_json):
        prompt += f"Element {i+1}:\n"
        for key, value in element.items():
            prompt += f"  - {key}: {json.dumps(value)}\n"
        prompt += "\n"
    
    prompt += "## AVAILABLE API ENDPOINTS (USE ONLY THESE):\n"
    
    # List all API endpoints with exact data
    for i, endpoint in enumerate(api_endpoints_json):
        prompt += f"Endpoint {i+1}:\n"
        for key, value in endpoint.items():
            prompt += f"  - {key}: {json.dumps(value)}\n"
        prompt += "\n"
    
    prompt += f"""## ALL {total_scenarios} GHERKIN SCENARIOS TO MAP (COMPLETE COVERAGE REQUIRED):
{feature_file_content}

## ABSOLUTE REQUIREMENTS:

### COMPLETE COVERAGE RULE:
- Map EVERY SINGLE scenario from above ({total_scenarios} total)
- Include EVERY SINGLE step ({total_steps} total) 
- Given, When, Then, And - ALL must be included
- Do NOT skip, summarize, or abbreviate any scenarios

### GIVEN STEP OBLIGATION (100% MANDATORY):
- EVERY Given step MUST specify URL: "URL is http://localhost:3000/[page]"
- Registration scenarios: "URL is http://localhost:3000/register"  
- Login scenarios: "URL is http://localhost:3000/login"
- Task scenarios: "URL is http://localhost:3000/tasks"
- Task creation: "URL is http://localhost:3000/tasks/new"

### ELEMENT USAGE RULES:
- Use ONLY Elements 1-{len(ui_elements_json)} with exact selectors
- Available selectors: {', '.join([elem.get('selector', 'N/A') for elem in ui_elements_json])}
- Do NOT invent: #register-link, #navbar-register, #task-creation-link, etc.

### API MAPPING RULES:
- Use ONLY Endpoints 1-{len(api_endpoints_json)}  
- Available URLs: {', '.join([endpoint.get('url', 'N/A') for endpoint in api_endpoints_json])}

## OUTPUT FORMAT (COMPLETE ALL {total_scenarios} SCENARIOS):

### SCENARIO: [Exact Scenario Name From Feature File]
| Step | Element(s) Used | Selector(s) | Action Type | API Triggered | Expected Data | Validation Method |
|------|----------------|-------------|-------------|---------------|---------------|-------------------|
| Given [complete step text] | Element X | [exact selector] | navigate | None | N/A | Page loads successfully, URL is http://localhost:3000/[page] |
| When [complete step text] | Element Y | [exact selector] | type/click | Endpoint Z | [data] | [validation] |
| Then [complete step text] | Element/None | [exact selector] | verify | Endpoint Z | [response] | [expected result] |
| And [complete step text] | Element W | [exact selector] | action | Endpoint/None | [data] | [validation] |

### LOGICAL MAPPING GUIDE:
- **User registration**: Elements 1,2,4 + Endpoint 1
- **User login**: Elements 1,2,3 + Endpoint 2  
- **Task operations**: Elements 6-11 + Endpoints 5,7,8,9
- **Navigation**: Element 5 (logout) + appropriate endpoints

## VERIFICATION CHECKLIST:
Before submitting, verify:
□ All {total_scenarios} scenarios are mapped
□ All {total_steps} steps are included
□ Every Given step has URL specification
□ Only provided elements/endpoints used
□ No invented selectors or URLs

## PROCESS ALL SCENARIOS NOW:
Generate complete mapping tables for EVERY scenario. Leave nothing out."""

    return prompt

def validate_scenario_completeness(llm_output, feature_content):
    """
    Validate that all scenarios and steps are included in the LLM output
    """
    # Parse original scenarios
    original_scenarios = parse_gherkin_scenarios(feature_content)
    
    issues = []
    scenario_count_in_output = 0
    step_count_in_output = 0
    
    # Count scenarios in output
    scenario_count_in_output = len(re.findall(r'### SCENARIO:', llm_output, re.IGNORECASE))
    
    # Count steps in output 
    step_count_in_output = len(re.findall(r'\| (Given|When|Then|And) ', llm_output, re.IGNORECASE))
    
    # Count original scenarios and steps
    original_scenario_count = len(original_scenarios)
    original_step_count = sum(len(scenario['steps']) for scenario in original_scenarios)
    
    print(f"📊 Scenario Coverage: {scenario_count_in_output}/{original_scenario_count}")
    print(f"📊 Step Coverage: {step_count_in_output}/{original_step_count}")
    
    # Check if all scenarios are present
    for scenario in original_scenarios:
        scenario_name = scenario['name'].strip()
        # More flexible matching for scenario names
        if not re.search(rf"### SCENARIO:.*{re.escape(scenario_name)}", llm_output, re.IGNORECASE):
            issues.append(f"Missing scenario: {scenario_name}")
        else:
            # Check if all steps are present for this scenario
            for step in scenario['steps']:
                step_type = step['type']
                step_text = step['text'][:50]  # First 50 chars for better matching
                # Look for this step in the output
                step_pattern = rf"\| {re.escape(step_type)}.*{re.escape(step_text[:20])}"
                if not re.search(step_pattern, llm_output, re.IGNORECASE):
                    issues.append(f"Missing step in '{scenario_name}': {step_type} {step_text}...")
    
    # Additional validation
    if scenario_count_in_output < original_scenario_count:
        issues.append(f"Only {scenario_count_in_output} scenarios mapped, need {original_scenario_count}")
    
    if step_count_in_output < original_step_count:
        issues.append(f"Only {step_count_in_output} steps mapped, need {original_step_count}")
    
    return issues

def generate_completeness_prompt(ui_elements_json, api_endpoints_json, feature_file_content, missing_items):
    """
    Generate a prompt to complete missing scenarios/steps
    """
    
    prompt = f"""CRITICAL: You missed several scenarios and steps. Complete ALL missing items below.

## WHAT YOU MISSED:
{chr(10).join(missing_items)}

## COMPLETE SCENARIO LIST (MAP ALL OF THESE):
{feature_file_content}

## AVAILABLE ELEMENTS (USE ONLY THESE WITH EXACT SELECTORS):
"""
    
    for i, element in enumerate(ui_elements_json):
        selector = element.get('selector', 'N/A')
        element_type = element.get('type', 'N/A') 
        text = element.get('text', element.get('placeholder', 'N/A'))
        prompt += f"Element {i+1}: selector=\"{selector}\" type=\"{element_type}\" text=\"{text}\"\n"
    
    prompt += f"""
## AVAILABLE ENDPOINTS (USE ONLY THESE WITH EXACT URLS):
"""
    
    for i, endpoint in enumerate(api_endpoints_json):
        method = endpoint.get('method', 'N/A')
        url = endpoint.get('url', 'N/A')
        prompt += f"Endpoint {i+1}: method=\"{method}\" url=\"{url}\"\n"
    
    prompt += f"""
## ABSOLUTE REQUIREMENTS:

### SCENARIO COMPLETION:
- Map EVERY scenario from the feature file above
- Include EVERY step: Given, When, Then, And
- No exceptions, no shortcuts

### GIVEN STEP URL REQUIREMENT:
- EVERY Given step MUST specify: "URL is http://localhost:3000/[page]"
- Examples:
  * Registration: "URL is http://localhost:3000/register"
  * Login: "URL is http://localhost:3000/login"  
  * Tasks: "URL is http://localhost:3000/tasks"
  * Task creation: "URL is http://localhost:3000/tasks/new"

### EXACT ELEMENT USAGE:
- Use ONLY Elements 1-{len(ui_elements_json)} with their exact selectors
- Do NOT invent: #register-link, #navbar-register, #task-creation-link etc.
- Use actual selectors: {', '.join([elem.get('selector', 'N/A') for elem in ui_elements_json[:5]])}...

### MAPPING TABLE FORMAT (FOR EVERY SCENARIO):

### SCENARIO: [Exact Scenario Name]
| Step | Element(s) Used | Selector(s) | Action Type | API Triggered | Expected Data | Validation Method |
|------|----------------|-------------|-------------|---------------|---------------|-------------------|
| Given [complete step text] | Element X | [exact selector] | navigate | None | N/A | Page loads, URL is http://localhost:3000/[page] |
| When [complete step text] | Element Y | [exact selector] | type/click | Endpoint Z | [data] | [validation] |
| Then [complete step text] | Element/None | [exact selector] | verify | Endpoint Z | [response] | [expected result] |
| And [complete step text] | Element W | [exact selector] | action | Endpoint/None | [data] | [validation] |

## GENERATE COMPLETE MAPPINGS NOW:
Create tables for ALL scenarios with ALL steps. Miss nothing."""
    
    return prompt

def generate_test_implementation_prompt(ui_elements_json, api_endpoints_json, feature_file_content):
    """
    Create a comprehensive test implementation prompt with completeness validation
    """
    
    # Parse scenarios for tracking
    scenarios = parse_gherkin_scenarios(feature_file_content)
    total_scenarios = len(scenarios)
    total_steps = sum(len(scenario['steps']) for scenario in scenarios)
    
    print(f"🎯 Target: {total_scenarios} scenarios with {total_steps} total steps")
    
    # First create the LLM-enhanced analysis prompt
    llm_prompt = create_llm_enhanced_prompt(ui_elements_json, api_endpoints_json, feature_file_content)
    
    # Run it through LLM to get intelligent mappings
    cmd = ['ollama', 'run', 'mistral', llm_prompt]
    
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
            llm_analysis = stdout.strip()
            
            # Validate completeness
            missing_items = validate_scenario_completeness(llm_analysis, feature_file_content)
            
            # If items are missing, run up to 2 completion attempts
            completion_attempts = 0
            max_attempts = 2
            
            while missing_items and completion_attempts < max_attempts:
                completion_attempts += 1
                print(f"⚠️ Attempt {completion_attempts}: Found {len(missing_items)} missing items. Completing...")
                
                completeness_prompt = generate_completeness_prompt(
                    ui_elements_json, api_endpoints_json, feature_file_content, missing_items
                )
                
                # Run completeness prompt
                cmd_complete = ['ollama', 'run', 'mistral', completeness_prompt]
                process_complete = subprocess.Popen(
                    cmd_complete,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                stdout_complete, stderr_complete = process_complete.communicate()
                
                if process_complete.returncode == 0:
                    # Append completion to original
                    llm_analysis = llm_analysis + f"\n\n## COMPLETION ATTEMPT {completion_attempts}:\n" + stdout_complete.strip()
                    
                    # Re-validate
                    missing_items = validate_scenario_completeness(llm_analysis, feature_file_content)
                    
                    if not missing_items:
                        print(f"✅ All scenarios completed on attempt {completion_attempts}")
                        break
                else:
                    print(f"⚠️ Completion attempt {completion_attempts} failed: {stderr_complete}")
                    break
            
            if missing_items:
                print(f"⚠️ Still missing {len(missing_items)} items after {completion_attempts} attempts")
                for item in missing_items:
                    print(f"   - {item}")
            else:
                print("✅ All scenarios and steps are complete")
            
            # Now create the final implementation prompt
            final_prompt = f"""You are an expert test automation engineer. Implement executable test code using the detailed mapping analysis below.

## DETAILED STEP-BY-STEP MAPPING ANALYSIS:
{llm_analysis}

## IMPLEMENTATION REQUIREMENTS:

### Test Framework Setup:
1. Use Selenium WebDriver for UI interactions
2. Use RestAssured or OkHttp for API testing  
3. Implement Page Object Pattern for UI elements
4. Create API client classes for endpoint interactions
5. Use TestNG or JUnit for test organization
6. Include proper setup/teardown methods

### For Each Mapped Step:
1. **UI Actions**: Use exact selectors provided in the mapping
2. **API Calls**: Use exact URLs and methods from the endpoint data
3. **Data Handling**: Use the postData examples as test data templates
4. **Validation**: Implement assertions based on responseBody examples
5. **Error Handling**: Add try-catch blocks for robust execution
6. **Waits**: Include explicit waits for element interactions

### Code Structure Requirements:
```java
// Example structure - adapt to your language
@Test
public void testScenarioName() {{
    // Given steps - setup/navigation with URL verification
    // When steps - user actions  
    // Then steps - validation
}}
```

### URL Management (CRITICAL):
- Every test must verify the correct URL after GIVEN steps
- Use WebDriver getCurrentUrl() to validate page location
- Navigate to specific pages as mapped in the analysis

### Authentication Flow:
- Use the authentication endpoints from the mapping
- Store tokens/session data for subsequent requests
- Handle login/logout flow as specified in scenarios

### Data Management:
- Create test data based on postData examples
- Use different data sets for positive/negative scenarios
- Handle dynamic IDs and responses appropriately

## COVERAGE VERIFICATION:
- Implementation must cover ALL {total_scenarios} scenarios
- Implementation must include ALL {total_steps} steps
- Every Given step must include URL verification
- Use only the exact selectors and endpoints from the mapping

## OUTPUT REQUIREMENTS:
Generate complete, executable test code that:
1. **Maps exactly to the analysis** - Follow the step mappings provided
2. **Uses exact selectors and endpoints** - No invented elements
3. **Includes ALL scenarios** - Complete implementation for EVERY mapped scenario
4. **Handles URL verification** - Validate page URLs after navigation
5. **Validates responses** - Assert against expected responseBody data
6. **Error handling** - Comprehensive exception handling
7. **Maintainable structure** - Clean, readable, maintainable code

Generate the complete test implementation now."""
            
            return final_prompt
        else:
            print(f"❌ LLM Error: {stderr}")
            # Fallback to basic implementation
            return create_basic_implementation_prompt(ui_elements_json, api_endpoints_json, feature_file_content)
            
    except Exception as e:
        print(f"❌ LLM Exception: {str(e)}")
        # Fallback to basic implementation
        return create_basic_implementation_prompt(ui_elements_json, api_endpoints_json, feature_file_content)

def create_basic_implementation_prompt(ui_elements_json, api_endpoints_json, feature_file_content):
    """
    Fallback basic implementation prompt if LLM fails
    """
    # Parse scenarios for counting
    scenarios = parse_gherkin_scenarios(feature_file_content)
    total_scenarios = len(scenarios)
    total_steps = sum(len(scenario['steps']) for scenario in scenarios)
    
    prompt = f"""You are an expert test automation engineer. Create executable test code using the provided data.

## COVERAGE REQUIREMENTS:
- Must implement ALL {total_scenarios} scenarios
- Must implement ALL {total_steps} steps  
- Every Given step must specify URL location

## UI ELEMENTS (USE EXACT SELECTORS):
"""
    
    for i, element in enumerate(ui_elements_json):
        selector = element.get('selector', 'N/A')
        element_type = element.get('type', 'N/A')
        prompt += f"Element {i+1}: {selector} ({element_type})\n"

    prompt += f"""
## API ENDPOINTS (USE EXACT URLS):
"""
    
    for i, endpoint in enumerate(api_endpoints_json):
        method = endpoint.get('method', 'N/A')
        url = endpoint.get('url', 'N/A')
        prompt += f"Endpoint {i+1}: {method} {url}\n"

    prompt += f"""
## ALL SCENARIOS TO IMPLEMENT:
{feature_file_content}

## REQUIREMENTS:
1. **Complete Coverage**: Implement every scenario and step
2. **URL Verification**: Every Given step must verify page URL
3. **Exact Elements**: Use only provided selectors and endpoints
4. **No Shortcuts**: Map all Given, When, Then, And steps

Generate complete test implementation using ONLY the exact selectors and endpoints provided above.
Ensure ALL {total_scenarios} scenarios are covered with ALL {total_steps} steps implemented."""
    
    return prompt

def run_test_prompt_generator(ui_file_path, api_file_path, feature_file_path):
    """
    Load all data files and generate the test implementation prompt using Ollama
    """
    
    try:
        # Load JSON files
        with open(ui_file_path, 'r', encoding='utf-8') as f:
            ui_data = json.load(f)
        
        with open(api_file_path, 'r', encoding='utf-8') as f:
            api_data = json.load(f)
            
        # Load feature file
        with open(feature_file_path, 'r', encoding='utf-8') as f:
            feature_content = f.read()
        
        print("🚀 Starting Generic Black Box Test Generator")
        print(f"📁 UI Elements: {len(ui_data)} items")
        print(f"📁 API Endpoints: {len(api_data)} items")  
        print(f"📁 Feature File: {feature_file_path}")
        
        # Parse and show scenario count
        scenarios = parse_gherkin_scenarios(feature_content)
        total_steps = sum(len(scenario['steps']) for scenario in scenarios)
        print(f"🎯 Target: {len(scenarios)} scenarios, {total_steps} steps")
        print("-" * 60)
        
        # Generate the test implementation prompt
        generated_prompt = generate_test_implementation_prompt(ui_data, api_data, feature_content)
        
        # Save the generated prompt
        with open('test_implementation_prompt.txt', 'w', encoding='utf-8') as f:
            f.write(generated_prompt)
        
        print("-" * 60)
        print("✅ Test implementation prompt saved to: test_implementation_prompt.txt")
        print(f"📄 Prompt length: {len(generated_prompt)} characters")
        print("\n" + "="*60)
        print("GENERATED TEST IMPLEMENTATION PROMPT:")
        print("="*60)
        print(generated_prompt[:2000] + "..." if len(generated_prompt) > 2000 else generated_prompt)
        
        return generated_prompt
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

# Example usage with file paths
if __name__ == "__main__":
    ui_file = r"C:\Users\Selim\OneDrive\Bureau\ai test\testo\ui_elements.json"
    api_file = r"C:\Users\Selim\OneDrive\Bureau\ai test\testo\api_calls.json"
    feature_file = r"C:\Users\Selim\OneDrive\Bureau\ai test\model\generated_tests.feature"
    
    # Generate test implementation prompt
    generated_prompt = run_test_prompt_generator(ui_file, api_file, feature_file)
    
    if generated_prompt:
        print(f"\n✅ Generic black box test implementation prompt ready!")
        print("📁 File: test_implementation_prompt.txt")
        print("\n🎯 This maps each Gherkin step to your EXACT selectors and APIs!")
        print("🔄 Can be used with any application by changing the JSON files!")