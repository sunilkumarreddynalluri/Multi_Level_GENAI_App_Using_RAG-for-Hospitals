# 🏥 Vihara Hospital — Multi-Department AI Assistant (RAG)

A multi-department, Retrieval-Augmented Generation (RAG) powered AI assistant for a hospital.
Each department (Reception, Billing, Insurance, Cardiology, Neurology, Pharmacy, Emergency) has
its **own isolated vector database**, so the AI only answers from that department's knowledge
base — reducing hallucination and keeping answers scoped and relevant.

Built with **Flask**, **LangChain**, **OpenAI**, and **ChromaDB**.

---

## ✨ Features

- 🗂️ **Multi-level RAG** — a separate Chroma vector store per department, instead of one giant mixed index
- 💬 Simple web UI to pick a department and ask a question in plain English
- 🤖 Answers are generated **only from the retrieved context** (the prompt explicitly restricts the LLM to the provided documents)
- 🏥 Seeded with realistic (synthetic) hospital data across 7 departments: Reception, Billing, Insurance, Cardiology, Neurology, Pharmacy, Emergency

> ⚠️ All hospital, patient, and clinical data included in this repo is **synthetic demo data** generated for learning/portfolio purposes only. It is **not** real patient information and must never be used for actual clinical or billing decisions.

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| LLM | OpenAI `gpt-4o` (via `langchain-openai`) |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector Store | ChromaDB (one collection per department) |
| Orchestration | LangChain (`langchain-core`, `langchain-classic`, `langchain-text-splitters`) |
| Frontend | HTML + CSS (Jinja2 templates) |

---

## 📁 Project Structure

```
Multi_Level_GENAI_App_Using_RAG/
├── app.py                  # Flask web app — serves the UI and answers questions
├── developer.py             # One-time ingestion script — builds the vector DBs from /data
├── requirements.txt         # Python dependencies
├── .env                     # Your OpenAI API key (you create this — not committed to git)
├── data/                    # Raw .txt knowledge files per department (input for developer.py)
│   ├── 01_reception.txt
│   ├── 02_billing.txt
│   ├── 03_insurance.txt
│   ├── 04_cardiology.txt
│   ├── 05_neurology_brain_tumor.txt
│   ├── 06_pharmacy.txt
│   └── 07_emergency.txt
├── db/                      # Auto-generated Chroma vector stores (created by developer.py)
├── templates/
│   └── index.html           # Main UI page
└── static/
    └── style.css             # Styling
```

---

## ✅ Prerequisites

- **Python 3.10+** installed ([python.org/downloads](https://www.python.org/downloads/))
- An **OpenAI API key** with available credits
- Git (optional, for cloning)

---

## 🔑 Getting an OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com/) and sign up or log in.
2. Click your profile icon (top-right) → **API keys** (or go directly to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)).
3. Click **"Create new secret key"**, give it a name, and copy the key immediately — OpenAI only shows it once.
4. Go to **Billing** ([platform.openai.com/settings/organization/billing](https://platform.openai.com/settings/organization/billing)) and add a payment method / credits. This project uses `gpt-4o` and `text-embedding-3-small`, both of which are paid, metered APIs — the free trial credit (if any) is usually enough for testing this project.
5. Keep the key private. Never commit it to GitHub — that's what the `.env` file (excluded via `.gitignore`) is for.

---

## 🚀 Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Multi_Level_GENAI_App_Using_RAG
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` appear at the start of your terminal prompt once it's active.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key

Create a file named exactly **`.env`** (with the leading dot, no other extension) in the project root:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

> 🛑 Common mistake: naming the file `env` instead of `.env`. `python-dotenv` only looks for a file literally called `.env` — without the leading dot, your key won't load and the app will crash with a `TypeError`.

### 5. Build the vector databases (run once, or whenever `/data` changes)

This reads every `.txt` file in `data/`, splits it into chunks, embeds each chunk with OpenAI, and saves a separate Chroma database per department into `db/`.

```bash
python developer.py
```

You should see console output like:
```
Data Collected Successfully from : 01_reception.txt : file
Number of Chunks in : 01_reception.txt : File was : 42
DB created Successfully for : 01_reception.txt
...
ALL DB created Successfully
```

This step calls the OpenAI Embeddings API, so it will use a small amount of API credit and may take a minute or two depending on data size.

### 6. Run the app

```bash
python app.py
```

Then open your browser to:

```
http://127.0.0.1:5000
```

Select a department, type a question (e.g. *"What are the OPD timings?"* for Reception, or *"What is the advance deposit for ICU?"* for Billing), and click **Ask AI Assistant**.

---

## 🔄 How It Works

1. **Ingestion (`developer.py`)** — Each department's `.txt` file is loaded, split into ~300-character overlapping chunks (`RecursiveCharacterTextSplitter`), embedded with `text-embedding-3-small`, and stored in its own Chroma collection under `db/<filename> database/`.
2. **Query (`app.py`)** — When a user submits a question:
   - The selected department's Chroma DB is loaded.
   - A similarity search retrieves the top 3 most relevant chunks (`k=3`).
   - Those chunks are passed as `context` into a prompt template alongside the user's `question`.
   - `gpt-4o` generates an answer **restricted to that context only** (via `create_stuff_documents_chain`), which is rendered back in the UI.

This "one vector DB per department" design is what makes it *multi-level* RAG — it avoids a Cardiology question accidentally retrieving Pharmacy chunks, and keeps each department's answers grounded in only its own knowledge base.

---

## 🛠️ Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` (or similar) | Run `pip install -r requirements.txt` inside the activated `.venv` |
| `TypeError: str expected, not NoneType` on `os.environ["OPENAI_API_KEY"]` | Your `.env` file is missing, misnamed (check for the leading dot), or in the wrong folder. It must sit next to `app.py`. |
| `openai.AuthenticationError` / `401` | Your API key is invalid, expired, or has no billing/credits attached — check [platform.openai.com/api-keys](https://platform.openai.com/api-keys) and billing. |
| App runs but every answer is empty/irrelevant | Make sure you ran `python developer.py` **before** `python app.py`, so the `db/` folder actually has data in it. |
| `where python` shows the global interpreter instead of `.venv` | Your virtual environment isn't actually active — run `.venv\Scripts\activate` (Windows) again before installing/running. |

---

## 📌 Notes / Future Improvements

- Add a `.gitignore` for `.venv/`, `.env`, `__pycache__/`, and `db/` (vector DBs are usually regenerated locally rather than committed).
- Add source citations in the UI (e.g., "From: Billing FAQ, Section 3").
- Add chat history / multi-turn conversation memory per session.
- Add authentication before deploying publicly, since this currently has no access control.

---

## 📄 License

This project is provided for educational/portfolio purposes. All hospital and patient data is synthetic.
