import pdfplumber
import json
import subprocess
import tempfile
import time

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages)
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def run_ai_model(prompt):
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp:
            tmp.write(prompt)
            tmp.flush()
            tmp_name = tmp.name

        cmd = ['ollama', 'run', 'mistral', prompt]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        try:
            stdout, stderr = process.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            process.kill()
            print("AI model timed out.")
            return None

        if process.returncode != 0:
            print(f"AI model error:\n{stderr}")
            return None

        return stdout.strip()

    except Exception as e:
        print(f"AI call failed: {e}")
        return None

def enrich_steps_with_io(json_path, cahier_text, output_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        scenarios_data = json.load(f)

    for feature in scenarios_data['features']:
        for scenario in feature['scenarios']:
            for step in scenario['steps']:
                step_text = step['step']

                prompt = f"""
From the following documentation:
{cahier_text[:4000]}

What is the expected input, output, and type (either 'api' or 'ui') for this test step:
"{step_text}"

Reply in this JSON format:
{{
  "input": "....",
  "output": "....",
  "type": "api"  // or "ui"
}}

If not applicable, write "N/A".
"""

                print(f"Processing: {step_text}")
                ai_response = run_ai_model(prompt)

                if ai_response:
                    try:
                        result_json = json.loads(ai_response)
                        step['input'] = result_json.get('input', "N/A")
                        step['output'] = result_json.get('output', "N/A")
                        step['type'] = result_json.get('type', "N/A").lower()

                        # Validate type value to be either 'api', 'ui' or 'n/a'
                        if step['type'] not in ['api', 'ui', 'n/a']:
                            step['type'] = 'N/A'

                    except Exception as e:
                        print(f"Failed to parse AI response: {e}\nResponse was:\n{ai_response}")
                        step['input'] = "N/A"
                        step['output'] = "N/A"
                        step['type'] = "N/A"
                else:
                    step['input'] = "N/A"
                    step['output'] = "N/A"
                    step['type'] = "N/A"

                time.sleep(1)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scenarios_data, f, indent=4, ensure_ascii=False)

    print(f"Enriched JSON saved to {output_path}")

if __name__ == "__main__":
    cahier_pdf_path = r"C:\Users\Selim\OneDrive\Bureau\ai test\docs\cahier1.pdf"
    json_input_path = "scenarios_with_io_placeholders.json"
    json_output_path = "scenarios_with_enriched_io_and_type.json"

    cahier_text = extract_text_from_pdf(cahier_pdf_path)
    enrich_steps_with_io(json_input_path, cahier_text, json_output_path)
