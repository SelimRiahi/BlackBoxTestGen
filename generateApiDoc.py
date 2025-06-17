import ollama
import os
import pdfplumber
import base64
from io import BytesIO
import textwrap
import re

# === Step 1: Extract full content from PDF ===
def extract_text_from_pdf(pdf_path):
    full_text = ""
    image_count = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                full_text += f"\n--- Page {page_number} TEXT ---\n{text.strip()}\n"

            tables = page.extract_tables()
            for idx, table in enumerate(tables):
                full_text += f"\n--- Page {page_number} TABLE {idx+1} ---\n"
                for row in table:
                    clean_row = [str(cell).strip() if cell else "" for cell in row]
                    full_text += " | ".join(clean_row) + "\n"

            if page.images:
                for img_index, img in enumerate(page.images):
                    image_count += 1
                    cropped = page.within_bbox((img['x0'], img['top'], img['x1'], img['bottom']))
                    im = cropped.to_image(resolution=150).original
                    buffered = BytesIO()
                    im.save(buffered, format="PNG")
                    img_b64 = base64.b64encode(buffered.getvalue()).decode()
                    full_text += (
                        f"\n--- Page {page_number} IMAGE {img_index + 1} ---\n"
                        f"[Image {image_count}] Base64 PNG (first 100 chars):\n"
                        f"{img_b64[:100]}... (truncated)\n"
                    )

    return full_text.strip()


# === Step 2: Use fixed prompt exactly as you wrote ===
def build_prompt_chunk(chunk_text):
    return f"""
You are an API design expert.

Your task is to generate a complete REST API documentation from the following functional and non-functional requirements extracted from a PDF. The source may include paragraphs, tables, and images (with descriptions or base64 placeholders).

## Guidelines:
- DO NOT invent features or endpoints that are not explicitly described or implied from structured data.
- DO NOT assume any backend technology (Node.js, Express, Spring Boot, etc.) unless it is **clearly mentioned** in the text, tables, or diagrams.
- If the framework, database, or port is not mentioned, leave those fields empty.
- If mentioned (even in a table or diagram), **detect and extract the actual technology used**.
- Map every **functional requirement**, including those inside tables or diagrams, to one or more relevant API endpoints.
- Include all standard CRUD operations (POST, GET, PUT, PATCH, DELETE) for each resource unless restricted in the document.
- Treat tables as **structured field definitions**: extract field names, types, constraints, optionality, etc.
- For diagrams or UI mockups: only infer endpoints if behavior or flow is clearly described or labeled.
- Use realistic field names and naming conventions based on context.

## Output per feature/resource:
For each endpoint, include:
- HTTP method and route
- JSON request schema (required vs optional fields)
- Example of a successful response
- Possible error codes and their causes
- Response headers if mentioned

## RAW PDF CONTENT:
{chunk_text}

## OUTPUT FORMAT:

API Documentation:
Framework: [Extracted if explicitly mentioned]
Database: [Extracted if explicitly mentioned]
Default Port: [Extracted if explicitly mentioned]

[Endpoints organized by resource]

## EXAMPLE (FORMAT ONLY – DO NOT COPY CONTENT):
API Documentation:
Framework: Spring Boot
Database: PostgreSQL
Default Port: 8080

Authentication:
- POST /register
  Request: {{
    "username": string (3-30 chars),
    "password": string (min 8 chars)
  }}
  Success: 201 Created + user object
  Errors: 400 Bad Request (validation), 409 Conflict (user exists)

Tasks:
- GET /tasks
  Success: 200 OK + [task objects]
  Errors: 401 Unauthorized

- POST /tasks
  Request: {{
    "title": string (required),
    "dueDate": ISO8601 date,
    "priority?": "low" | "medium" | "high"
  }}
  Success: 201 Created + task object
  Errors: 400 Bad Request

[... continue with other endpoints]

Response Headers:
- Content-Type: application/json
- X-Response-Time: <milliseconds>
""".strip()


# === Cleaning and merging logic ===
def clean_and_merge_output(text):
    parts = re.split(r"\n+-{3,} Part \d+ -{3,}\n", text)
    seen_lines = set()
    cleaned_lines = []

    for part in parts:
        lines = part.splitlines()
        for line in lines:
            normalized = line.strip()
            if normalized and normalized not in seen_lines:
                seen_lines.add(normalized)
                cleaned_lines.append(normalized)

    return "\n".join(cleaned_lines)


# === Step 3: Main generation logic with chunking ===
def generate_api_docs_from_pdf(pdf_path):
    full_text = extract_text_from_pdf(pdf_path)

    # Split into chunks (adjust based on model capacity)
    max_chunk_len = 7000  # tokens approximation in characters
    chunks = textwrap.wrap(full_text, max_chunk_len, break_long_words=False, break_on_hyphens=False)

    final_output = ""
    for i, chunk in enumerate(chunks, start=1):
        print(f"🧠 Sending chunk {i}/{len(chunks)} to Ollama...")

        prompt = build_prompt_chunk(chunk)
        response = ollama.generate(
            model="mistral",
            prompt=prompt,
            options={"temperature": 0.3, "num_ctx": 8192}
        )

        final_output += f"\n\n--- Part {i} ---\n{response['response'].strip()}"

    # Clean and merge
    cleaned_output = clean_and_merge_output(final_output)

    # Write result
    os.makedirs("generated_docs", exist_ok=True)
    output_path = "generated_docs/api_docs.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_output.strip())

    print(f"✅ Cleaned API Documentation saved at {output_path}")


# === Step 4: Run the script ===
if __name__ == "__main__":
    generate_api_docs_from_pdf("docs/cahier_de_charge.pdf")