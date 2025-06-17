# 📄 Cahier des Charges Cleaner with Ollama + Mistral

This Python project processes a **cahier des charges** (requirements document) PDF by extracting, cleaning, and organizing functional and non-functional requirements using AI models like Mistral (via Ollama) and transformer-based NLP tools.

It splits the document into chunks, sends each to AI for extraction, caches results, merges all parts, then cleans and deduplicates the requirements for a clear, concise final output.

---

## 🧠 What this Project Does

- 📥 **Loads a PDF file** containing functional and technical specifications.  
- ✂️ **Splits the text into smaller chunks** for easier AI processing.  
- 🤖 **Uses Llama3 (via Ollama)** to extract functional and non-functional requirements from each chunk.  
- 💾 **Caches results locally** to avoid reprocessing the same chunks repeatedly.  
- 🔄 **Merges all extracted chunks** into one organized file named `exigences_organisees.txt`.  
- 🔍 **Runs NLP and paraphrase models** to clean, simplify, and remove duplicate or very similar requirements from the merged file.  
  - Uses a French NLP model (`fr_core_news_lg`) to parse and simplify sentences by focusing on core grammatical parts.  
  - Uses a paraphrase detection model (`paraphrase-mpnet-base-v2`) to identify and remove redundant requirements.  

---

## 🗂️ Files and What They Do

- `generate_cahier.py`  
  Splits the input PDF into chunks, processes each chunk with the AI extraction model, and merges all outputs into one organized requirements file.

- `transformer.py`  
  Cleans the merged requirements using NLP parsing and paraphrase detection to simplify sentences and remove duplicates or redundancies.

- `multithread.py`  
  Finds the best number of threads to send parallel requests to the AI model to optimize speed.

---

## ⚠️ Known Issues
-the result has improved but:
- 🔄 **Précision partielle : Le modèle NLP utilisé est précis à environ 85 %, ce qui signifie qu’il reste une marge d'amélioration.
🧹 Détails hors-sujet : Des informations peu pertinentes ou secondaires peuvent parfois être conservées à tort.
---

## 📂 Test Document

The project was tested with `cahier1.pdf`, a 20-page real-world cahier des charges with rich formatting and detailed project specifications.

---

# Usage


2. Run `generate_cahier.py` to extract and merge requirements.  
ignore verifier_exigences.py
---


