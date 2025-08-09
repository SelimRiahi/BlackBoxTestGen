import subprocess
import json
import re
from pathlib import Path

class PlaywrightTestGenerator:
    def __init__(self, test_data_path, feature_file_path, output_dir="generated_tests"):
        self.test_data = self._load_json(test_data_path)
        self.scenarios = self._load_feature_file(feature_file_path)
        self.output_dir = Path(output_dir)
        self.model = "mistral"
        
    def _load_json(self, path):
        with open(path) as f:
            return json.load(f)
    
    def _load_feature_file(self, path):
        with open(path) as f:
            return f.read()
    
    def _extract_patterns(self):
        """Identify UI and API patterns without domain assumptions"""
        patterns = {
            "auth_elements": [],
            "crud_elements": [],
            "auth_endpoints": [],
            "crud_endpoints": [],
            "dynamic_selectors": [],
            "ui_states": set()
        }
        
        # Analyze UI elements
        for el in self.test_data["uiElements"]:
            el_id = el["id"].lower()
            if any(kw in el_id for kw in ["auth", "login", "register", "logout"]):
                patterns["auth_elements"].append(el["id"])
            else:
                element_pattern = el["id"].split('-')[0]
                if "dynamicProperties" in el:
                    element_pattern += "-{{ID}}"
                    patterns["dynamic_selectors"].append(el["dynamicProperties"]["pattern"])
                patterns["crud_elements"].append(element_pattern)
        
        # Analyze API calls
        for call in self.test_data["apiCalls"]:
            url = call["url"].lower()
            endpoint = f"{call['method']} {call['url'].split('?')[0].split('/')[-1]}"
            
            if any(kw in url for kw in ["auth", "login", "register"]):
                patterns["auth_endpoints"].append(endpoint)
            else:
                patterns["crud_endpoints"].append(endpoint)
        
        # Extract UI states
        for state in self.test_data["uiStateHistory"]:
            patterns["ui_states"].add(state["action"].replace("API_CALL_", ""))
        
        patterns["ui_states"] = list(patterns["ui_states"])
        return patterns
    
    def _generate_llm_prompt(self, patterns):
        """Create strict blackbox prompt for test generation"""
        return f"""
Generate Playwright test code following STRICT BLACKBOX principles:

RULES:
1. NEVER assume application functionality or domain
2. Use ONLY these element patterns and API endpoints
3. Treat all elements as generic resources
4. Handle dynamic selectors using these patterns: {patterns['dynamic_selectors']}
5. Structure tests using Page Object Model
6. Include both UI and API assertions

ELEMENTS:
- Authentication: {patterns['auth_elements']}
- CRUD Operations: {patterns['crud_elements']}

ENDPOINTS:
- Authentication: {patterns['auth_endpoints']}
- CRUD Operations: {patterns['crud_endpoints']}

UI STATES OBSERVED: {patterns['ui_states']}

GHERKIN SCENARIOS:
{self.scenarios}

OUTPUT REQUIREMENTS:
1. Single file containing all test code
2. Use async/await Playwright syntax
3. Include these sections:
   // PAGE OBJECTS
   [Page class implementations...]
   
   // TEST FIXTURES
   [Test setup/teardown...]
   
   // TEST CASES
   [Test implementations...]
   
   // HELPER FUNCTIONS
   [Dynamic selector helpers...]
"""

    def _call_ollama(self, prompt):
        """Execute Ollama with the given prompt"""
        cmd = ["ollama", "run", self.model, prompt]
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
            return stdout if process.returncode == 0 else None
        except Exception as e:
            print(f"Ollama execution failed: {e}")
            return None
    
    def _extract_test_code(self, output):
        """Extract the JavaScript code from LLM output"""
        start_marker = "```javascript"
        end_marker = "```"
        start_idx = output.find(start_marker)
        end_idx = output.rfind(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            return output[start_idx+len(start_marker):end_idx].strip()
        return output
    
    def _save_test_file(self, content):
        """Save the generated test file"""
        self.output_dir.mkdir(exist_ok=True)
        output_path = self.output_dir / "playwright_tests.js"
        
        with open(output_path, "w") as f:
            f.write(content)
        print(f"Tests generated at: {output_path}")
    
    def generate(self):
        """Main generation workflow"""
        print("Analyzing test data patterns...")
        patterns = self._extract_patterns()
        
        print("Generating LLM prompt...")
        prompt = self._generate_llm_prompt(patterns)
        
        print("Generating tests with Ollama...")
        llm_output = self._call_ollama(prompt)
        
        if llm_output:
            print("Processing generated code...")
            test_code = self._extract_test_code(llm_output)
            
            if test_code:
                self._save_test_file(test_code)
                print("Test generation completed successfully!")
            else:
                print("Failed to extract test code from LLM output")
        else:
            print("Test generation failed")

if __name__ == "__main__":
    generator = PlaywrightTestGenerator(
        test_data_path="test_data.json",
        feature_file_path="generated_tests.feature"
    )
    generator.generate()