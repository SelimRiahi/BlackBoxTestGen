# Blackbox Test Generator with Node.js & Ollama

This project demonstrates how to automatically generate blackbox tests for a Node.js backend using [Ollama](https://ollama.com/) with the Mistral model, and MongoDB as the database.

## 📦 Project Structure

- `backend/` – A simple Node.js + Express app with MongoDB for task management (create/list tasks).
  - `.env` – MongoDB connection string (`MONGODB_URI=mongodb://localhost:27017/taskdb`)
  - Launches both the backend server and connects to MongoDB (`mongod` should be running).

- `docs/` – Contains:
  - `api_docs.txt` – Description of available backend API routes.
  - `requirements.txt` – Functional requirements (used for generating test cases).

- `generated_tests/` – Stores the test file created by the script.

- `generate_tests.py` – Python script that:
  1. Reads `docs/`
  2. Sends a prompt to Ollama (with Mistral)
  3. Generates blackbox tests using `pytest` and saves them to `generated_tests/test_api.py`

## 🧠 Dependencies

- Node.js & Express
- MongoDB (`mongod` must be running)
- Python 3
- Ollama with the `mistral` model installed

