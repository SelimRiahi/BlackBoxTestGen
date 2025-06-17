#📄 REST API Generator from Cahier des Charges with Ollama + Mistral  
This Python project automatically generates REST API documentation from a PDF cahier des charges (requirements document) using the Mistral model via Ollama.

It extracts text, tables, and images, splits the content into chunks to respect LLM token limits, sends each chunk to the AI, then merges and cleans the results into a complete API doc.

---

##🧠 What this Project Does  
-📥 Loads a PDF file of a functional/technical specification.  
-🔍 Extracts paragraphs, tables (as field definitions), and images (base64 placeholders).  
-✂️ Chunks the text to avoid exceeding model context limits.  
-🧹 Uses a fixed prompt to generate REST API endpoints, schemas, errors, and response examples.  
-💾 Saves the final cleaned and merged API documentation locally.  

---

##⚠️ Known Limitations  
-🧪 Some API details might be missed if content is vague or only in images without description.  
-🧱 Requires Ollama installed and running with the mistral model.  

---

##🧠 Dependencies  
- Python 3.8+  
- pdfplumber  
- ollama Python client
