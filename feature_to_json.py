import re
import json

def parse_feature_file_with_placeholders(feature_path):
    with open(feature_path, 'r', encoding='utf-8') as f:
        content = f.read()

    features = []
    feature_blocks = re.split(r'Feature:', content)[1:]  # Ignore anything before first 'Feature:'

    for block in feature_blocks:
        lines = block.strip().split('\n')
        feature_name = lines[0].strip()
        scenarios = []
        current_scenario = None
        steps = []

        for line in lines[1:]:
            line = line.strip()
            if line.startswith('Scenario:'):
                if current_scenario:
                    scenarios.append({
                        'scenario_name': current_scenario,
                        'steps': steps
                    })
                current_scenario = line.replace('Scenario:', '').strip()
                steps = []
            elif any(line.startswith(k) for k in ['Given', 'When', 'Then', 'And']):
                steps.append({
                    'step': line,
                    'input': "",
                    'output': "",
                    'type': "",
                    'locator': "",
                    'endpoint': "",
                    'expected_status': "",
                    "expected_response": {}
                })

        if current_scenario:
            scenarios.append({
                'scenario_name': current_scenario,
                'steps': steps
            })

        features.append({
            'feature_name': feature_name,
            'scenarios': scenarios
        })

    return features

if __name__ == "__main__":
    feature_file_path = "test_scenarios.feature"
    output_json_path = "scenarios_with_io_placeholders.json"

    structured_features = parse_feature_file_with_placeholders(feature_file_path)

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump({"features": structured_features}, f, indent=4, ensure_ascii=False)

    print(f"Structured JSON with full placeholders saved to {output_json_path}")
