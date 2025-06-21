# 📄 Cahier des Charges Cleaner with Ollama + LLAMA

This Python project helps clean up a **cahier des charges** (a project requirements document). It uses AI to find and organize the FUNCTIONAL requirements from a PDF file.


---

## 🧠 What this Project Does

- 📥 **Reads a PDF file** that contains project requirements.
- ✂️ **Splits the PDF into smaller parts** (chunks) to make AI processing easier.
- 🤖 **Uses llama via Ollama** to extract both **functional** and **non-functional** requirements.
- 💾 **Saves (caches) the results locally**, so you don’t have to repeat extractions.
- 📝 **Merges all parts into one file** called `exigences_organisees.txt`.
- 🧠 **Cleans and filters the final file** using smart AI tools:
  - ✅ **Uses Sentence Transformers** to compare every requirement with the others and detect duplicates or very similar ideas.
  - 🔍 **Uses NLI (Natural Language Inference)** to check if one sentence means the same thing as another, even if it's written differently.
  - 🧹 **Removes duplicates or repeated ideas** to keep only the clearest version.

---

## 🗂️ Files and What They Do

- `generate_cahier.py`  
  Splits the PDF, sends each part to AI, and merges the results.

- `transformer.py`  
  Uses NLP and NLI models to clean and remove duplicate or repeated requirements.
- `similarity_log.txt`  (related to `transformer.py`  )
This is a log from the **Sentence Transformer model** (`paraphrase-mpnet-base-v2`).  
It compares all the sentences to check how similar they are.  
If two sentences are **more than 90% similar** (score > 0.9), the **shorter one is removed**.  
This helps reduce repeated or duplicate ideas.
- `nli_log.txt`  (related to `transformer.py`  )
  This is a log from the **NLI model** (`joeddav/xlm-roberta-large-xnli`).  
  It checks if one sentence **means the same thing** as another.  
  If the model is very sure (score > 0.9), the **shorter sentence is removed**.  
  This helps keep only the most complete version of each requirement.)
- `multithread.py`  
  Helps speed up the process by running tasks in parallel using multiple threads.

---

## ⚠️ IIIIIIIIIIssues

- 🧾 **After the LLaMA model step**: Some content is kept even though it’s **not really a functional ** (this is likely due to prompt limitations).
- ❗ **In the cleaning phase (`transformer.py`)**:  
  The use of **Sentence Transformers + NLI** is **sometimes too aggressive** — it can wrongly delete a sentence that has **a different meaning**, thinking it's a duplicate.
---

## 📂 Test Document

This tool was tested on `cahier1.pdf`, a real-world 20-page document with complex structure and formatting.

---

## 🚀 How to Use

-Run `GenerateCahier.py`

> ℹ️ Ignore `verifier_exigences.py` — it’s not needed for now.
