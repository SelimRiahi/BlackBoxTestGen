import json
from pathlib import Path
from urllib.parse import urlparse

# Paths
api_path = Path(r"C:\Users\Selim\OneDrive\Bureau\ai test\testo\api_calls.json")
ui_path = Path(r"C:\Users\Selim\OneDrive\Bureau\ai test\testo\ui_elements.json")
output_path = Path(r"C:\Users\Selim\OneDrive\Bureau\ai test\testo\enhanced_blueprint.json")

# Load files
with api_path.open(encoding="utf-8") as f:
    api_calls = json.load(f)

with ui_path.open(encoding="utf-8") as f:
    ui_elements = json.load(f)

# Match a UI input field based on name
def find_input_selector(field_name):
    field_name_lower = field_name.lower()
    for el in ui_elements:
        if el["tag"] == "input" and el["visible"]:
            # Match against name/id/placeholder
            if field_name_lower in el.get("name", "").lower():
                return el["selector"]
            if field_name_lower in el.get("id", "").lower():
                return el["selector"]
            if field_name_lower in el.get("placeholder", "").lower():
                return el["selector"]
    # fallback to a visible text input
    for el in ui_elements:
        if el["tag"] == "input" and el["type"] == "text" and el["visible"]:
            return el["selector"]
    return "#unknown-input"

# Find a button selector based on current route
def find_button_for_path(route):
    for el in ui_elements:
        if el["tag"] == "button" and el["visible"] and el.get("type") == "submit":
            return el["selector"]
    return "#submit-button"

# Scenario generator
def generate_scenario(call):
    parsed = urlparse(call["url"])
    path = parsed.path
    method = call["method"]
    data = json.loads(call["postData"]) if call["postData"] else {}

    steps = [{"type": "navigate", "target": path}]
    
    for key, value in data.items():
        selector = find_input_selector(key)
        steps.append({
            "type": "input",
            "target": selector,
            "value": value
        })

    btn_selector = find_button_for_path(path)
    steps.append({
        "type": "click",
        "target": btn_selector
    })

    steps.append({
        "type": "assert",
        "target": "response_status",
        "value": call["status"]
    })

    return {
        "title": f"Scenario for {method} {path}",
        "steps": steps
    }

# Main generation
scenarios = []
for call in api_calls:
    if call["method"] in ["POST", "DELETE"] or (call["method"] == "GET" and "/tasks" in call["url"]):
        scenarios.append(generate_scenario(call))

# Save output
with output_path.open("w", encoding="utf-8") as f:
    json.dump(scenarios, f, indent=2)

print(f"✅ Generated {len(scenarios)} clean scenarios in: {output_path}")
