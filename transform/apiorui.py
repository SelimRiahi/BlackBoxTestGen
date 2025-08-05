import json
import re
import sys
from pathlib import Path

class StepClassifier:
    """Ultimate UI/API step classifier with precise pattern matching"""
    
    # UI patterns with boosted weights for interaction terms
    UI_PATTERNS = {
        # Navigation and structure
        'page': 3, 'screen': 3, 'form': 3, 'dialog': 2,
        'button': 4, 'link': 3, 'field': 3, 'menu': 2,
        
        # User actions
        'click': 5, 'press': 4, 'type': 3, 'enter': 3,
        'select': 4, 'check': 4, 'submit': 3, 'navigate': 4,
        'hover': 2, 'scroll': 2, 'drag': 2, 'logged in': 3,
        
        # Visual feedback
        'see': 4, 'view': 3, 'display': 3, 'message': 3,
        'indicator': 3, 'visible': 3, 'redirect': 3, 'appear': 3
    }
    
    # API patterns with technical focus
    API_PATTERNS = {
        # Technical infrastructure
        'api': 6, 'endpoint': 6, 'status': 5, 'response': 5,
        'request': 4, 'header': 4, 'payload': 4, 'server': 3,
        
        # Data operations
        'create': 4, 'delete': 4, 'update': 4, 'store': 4,
        'persist': 4, 'retrieve': 3, 'remain': 3, 'saved': 3,
        'permanently': 4, 'database': 3,
        
        # System processes
        'authenticate': 4, 'authorize': 4, 'validate': 3,
        'process': 3, 'sync': 2
    }

    @classmethod
    def classify(cls, step_text: str) -> str:
        """Classify with enhanced context awareness"""
        step_lower = step_text.lower()
        
        # Priority 1: Absolute UI markers
        if any(re.search(rf"\b{term}\b", step_lower) 
               for term in ['click', 'button', 'see ', 'page']):
            return "UI"
            
        # Priority 2: Absolute API markers
        if any(re.search(rf"\b{term}\b", step_lower) 
               for term in [' api ', 'status', 'endpoint']):
            return "API"
        
        # Priority 3: Contextual patterns
        if re.search(r"should (?:see|view|display)", step_lower):
            return "UI"
        if re.search(r"(?:created|deleted|updated) (?:in|on) (?:backend|system)", step_lower):
            return "API"
        
        # Score calculation
        ui_score = sum(
            weight for term, weight in cls.UI_PATTERNS.items() 
            if re.search(rf"\b{term}\b", step_lower)
        )
        api_score = sum(
            weight for term, weight in cls.API_PATTERNS.items()
            if re.search(rf"\b{term}\b", step_lower)
        )
        
        # Decision with clear threshold
        return "API" if api_score > ui_score + 1 else "UI"


class BlueprintProcessor:
    """Robust JSON processor with error handling"""
    
    @staticmethod
    def validate_structure(data: dict) -> bool:
        """Ensure proper blueprint structure"""
        required_keys = {'scenarios', 'metadata'}
        if not all(key in data for key in required_keys):
            raise ValueError("Invalid blueprint structure")
        return True
    
    @staticmethod
    def process_file(input_path: str, output_path: str) -> bool:
        """Full processing pipeline"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            BlueprintProcessor.validate_structure(data)
            
            for scenario in data.get("scenarios", []):
                for step in scenario.get("steps", []):
                    if not step.get("type"):
                        step["type"] = StepClassifier.classify(step["gherkin_text"])
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"ERROR: {str(e)}", file=sys.stderr)
            return False


def main():
    DEFAULT_INPUT = "test_blueprint.json"
    DEFAULT_OUTPUT = "enhanced_blueprint.json"
    
    # Argument handling
    if len(sys.argv) == 1:
        print("Using default file paths:")
        print(f"Input: {DEFAULT_INPUT}")
        print(f"Output: {DEFAULT_OUTPUT}")
        input_file = DEFAULT_INPUT
        output_file = DEFAULT_OUTPUT
    elif len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print("Usage:")
        print(f"  {sys.argv[0]} [input.json output.json]")
        print("If no arguments, uses default file names")
        sys.exit(1)
    
    # Process with error handling
    if not Path(input_file).exists():
        print(f"Error: Input file not found - {input_file}", file=sys.stderr)
        sys.exit(1)
        
    success = BlueprintProcessor.process_file(input_file, output_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()