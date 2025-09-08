import os
from openai import OpenAI

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
# ⚠️ Remplace par ta vraie clé API Claude (Anthropic ou OpenAI wrapper)
os.environ["OPENAI_API_KEY"] = "YOUR_CLAUDE_API_KEY"

# Initialiser le client
client = OpenAI()

# ------------------------------------------------------------
# Charger le PDF à envoyer
# ------------------------------------------------------------
pdf_path = r"C:\Users\Selim\Downloads\cahier (6).pdf"

with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

# ------------------------------------------------------------
# Prompt à envoyer avec le PDF
# ------------------------------------------------------------
prompt = """
From this pdf which is "C:\\Users\\Selim\\Downloads\\cahier (6).pdf":

You are a QA engineer specializing in black-box Gherkin scenario generation for executable test automation.
You do not have access to the application's source code, backend, APIs, tokens, database, or any internal logic. You are only provided with the user-facing documentation.
Your task is to generate executable black-box Gherkin scenarios based solely on concrete user actions and observable outcomes described in the documentation.
Strict Rules:
What to INCLUDE:
* User actions only: clicking buttons, typing in fields, navigating pages
* Observable results only: visible messages, page redirections, content appearing/disappearing in UI
* Documented failure cases only: generate error scenarios ONLY if the documentation explicitly states when failures occur
* Required preconditions: always include necessary setup in Given steps (e.g., user must be logged in)
What to EXCLUDE:
* Backend processes, authentication tokens, database operations, API calls
* Technical implementation details (sessions, storage mechanisms, internal processes)
* UI behavior scenarios (loading states, visual highlighting, auto-refresh, validation feedback)
* Generic usability or interface testing scenarios
* Any scenarios not explicitly described in the documentation
Avoid Redundant Testing:
* Do NOT create separate viewing/listing scenarios if the functionality is already implicitly tested within other workflows
* Focus on core actions that change system state, not passive viewing operations
* Each scenario should test a unique user workflow - avoid testing the same functionality through different entry points
* If viewing/listing is a byproduct of another action (like seeing content after login, or seeing updated content after creation/deletion), do NOT create dedicated viewing scenarios
* Only test viewing functionality separately if it's a distinct feature with specific documented behavior that isn't covered by other workflows
Generation Requirements:
* For each documented feature, create:
   * ✅ One success scenario if success behavior is described
   * ❌ One failure scenario ONLY if failure conditions are explicitly documented
* Focus on state-changing actions (create, update, delete, login, logout)
* Eliminate redundant test coverage - if viewing happens during other workflows, don't create separate viewing tests
* Use concrete, testable steps that a test automation tool can execute
* Ensure each scenario tests a complete user workflow from start to finish
* Only generate scenarios for features explicitly mentioned in the provided documentation
Scenario Structure:
* Given: User's starting state and necessary preconditions
* When: Specific user actions performed
* Then: Observable outcomes that can be verified by automated tests
Generate only scenarios that represent complete, testable user journeys for core state-changing operations described in the documentation, avoiding any redundant test coverage of passive viewing functionality.
"""

# ------------------------------------------------------------
# Envoyer la requête à Claude via OpenAI wrapper
# ------------------------------------------------------------
response = client.chat.completions.create(
    model="claude-3-sonnet-20240229",  # Tu peux changer le modèle (ex: claude-3-opus)
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "file",
                    "file_data": {
                        "name": "cahier.pdf",
                        "mime_type": "application/pdf",
                        "data": pdf_bytes
                    }
                }
            ],
        },
    ],
)

# ------------------------------------------------------------
# Afficher la réponse
# ------------------------------------------------------------
print(response.choices[0].message["content"])
