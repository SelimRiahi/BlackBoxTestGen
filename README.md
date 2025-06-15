# 📄 Cahier des Charges Cleaner with Ollama + Mistral

This Python project takes a PDF cahier des charges (requirements document), cleans the text, and extracts functional and non-functional requirements using the Mistral model via Ollama.

It splits the document into small parts, sends each to the AI, and saves the results. It also uses caching to avoid repeating the same work.

---

## 🧠 What this Project Does

- 📥 **Loads a PDF file** of a functional/technical specification.
- ✂️ **Chunks the text** to avoid exceeding LLM token limits.
- 🧹 **Cleans each chunk** and asks the LLM to:
  - Remove names, titles, and useless info.
  - Reformulate the content.
  - Extract clear requirements.
- 💾 **Caches each result** locally so repeated runs are faster.

---

## 📂 Test Document

We tested the script with `cahier1.pdf`, a real 20-page _cahier des charges_. It includes rich formatting,  and real project specifications.

---

## ⚠️ Problems

- 🧪 **Imperfect Results**: When extracting functional and non-functional requirements, some **useless or irrelevant information** may still appear.

---
