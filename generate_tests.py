import pdfplumber
import subprocess
from textwrap import dedent
import time

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages)
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def generate_gherkin(pdf_path):
    # 1. Extract text
    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("No text extracted from PDF")
        return
    
    # 2. Prepare LLM prompt (limit size)
    prompt = dedent(f"""
    Extract test scenarios in Gherkin format from these requirements. 
    Focus on:
    - User actions
    - System responses
    - Validation rules
    - Error conditions
    
    Generate ONLY scenarios without explanations.
    
    Requirements:
    {text[:5000]}  # Reduced further to ensure prompt isn't too large
    """)
    
    # 3. Run Mistral via Ollama with proper encoding
    print("Generating test scenarios (this may take a few minutes)...")
    try:
        cmd = ['ollama', 'run', 'mistral', prompt]
        
        # Using Popen with explicit UTF-8 encoding
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'  # Will replace undecodable bytes
        )
        
        try:
            stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout
        except subprocess.TimeoutExpired:
            process.kill()
            print("Command timed out after 5 minutes")
            return
            
        if process.returncode != 0:
            print(f"Ollama failed with error:\n{stderr}")
            return
            
        # 4. Save output
        with open("test_scenarios.feature", "w", encoding="utf-8") as f:
            f.write(stdout)
        print("Successfully generated test_scenarios.feature")
        
    except Exception as e:
        print(f"Unexpected error: {e}")

# Execute
if __name__ == "__main__":
    pdf_path = r"C:\Users\Selim\OneDrive\Bureau\ai test\docs\cahier1.pdf"
    try:
        generate_gherkin(pdf_path)
    except Exception as e:
        print(f"Script failed: {e}")
