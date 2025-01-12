
# Personal Finance Management — Retrieval-Augmented Generation (RAG)

This repository contains a **Personal Finance Management** system that uses **OpenAI** (GPT) to answer queries about your financial documents. It leverages **semantic search** (via embeddings) and a **vector database** to store and retrieve document chunks. You can upload financial documents (e.g., bank statements), then ask natural language questions like “What is my closing balance?” and get detailed AI-generated answers.

---

## Features

- **Document Upload**  
  Upload your financial documents (e.g., PDF or text files) using a simple API or frontend UI.  
- **Semantic Search & Vector Embeddings**  
  Uses [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings) to transform financial text into vector representations, then stores them in PostgreSQL.  
- **RAG-Based Q&A**  
  Ask natural language questions about your uploaded bank statements. The system retrieves relevant document chunks and generates answers via GPT.  
- **Hardcoded Document Type**  
  For simplicity, every upload is automatically tagged as `bank_statement`, so no user-provided document type is needed.  
- **FastAPI**  
  Provides a clean, documented REST API at `/docs`.  
- **React Frontend (Optional)**  
  A lightweight React app for uploading files and asking queries.

---

## Tech Stack

- **Backend**  
  - [Python 3.9+](https://www.python.org/)  
  - [FastAPI](https://fastapi.tiangolo.com/)  
  - [SQLAlchemy / Alembic](https://www.sqlalchemy.org/)  
  - [OpenAI API](https://platform.openai.com/)  
  - [psycopg2 / PostgreSQL](https://www.postgresql.org/)  

- **Frontend** (Optional)
  - [React](https://reactjs.org/)  
  - [Tailwind CSS](https://tailwindcss.com/)  

---

## Project Structure

```
financial_management/
├── alembic/
│   ├── env.py                # Alembic environment & migration config
│   ├── script.py.mako        # Alembic template for new migrations
│   └── versions/             # Auto-generated migration files
├── app/
│   ├── main.py               # FastAPI entry point
│   ├── core/
│   │   └── config.py         # Settings / environment variables
│   ├── db/
│   │   ├── session.py        # SQLAlchemy session setup
│   │   └── models/
│   │       └── document.py   # Document & Embedding models
│   ├── schemas/
│   │   ├── document.py       # Pydantic models for Documents
│   │   └── query.py          # Pydantic models for Query
│   ├── services/
│   │   ├── openai_service.py # OpenAI usage (embeddings, chat completions)
│   │   └── document_service.py
│   └── api/
│       └── v1/
│           ├── router.py     # Main API router
│           └── endpoints/
│               ├── documents.py
│               └── analysis.py
├── frontend/ (Optional)
│   ├── src/
│   ├── public/
│   └── ...
├── requirements.txt          # Python dependencies
├── alembic.ini               # Alembic config
├── .env                      # Environment variables (Postgres, OpenAI key)
└── README.md                 # (This file)
```

---

## Setup & Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/yourusername/rag-finance-management.git
   cd rag-finance-management
   ```

2. **Create & Activate a Virtual Environment**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Linux/Mac
   # Windows:
   # venv\Scripts\activate
   ```

3. **Install Python Dependencies**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install & Start PostgreSQL**  
   - Make sure PostgreSQL is running locally.  
   - Create a new database:  
     ```bash
     psql -U postgres
     CREATE DATABASE finance_database;
     ```

5. **Configure Environment Variables (`.env`)**  
   Create a file named `.env` in the project root with the following content (example):
   ```ini
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_SERVER=localhost
   POSTGRES_DB=finance_database
   OPENAI_API_KEY=sk-xxxxxx   # Replace with your actual OpenAI API key
   ```

6. **Run Database Migrations**  
   ```bash
   alembic upgrade head
   ```
   This will create all necessary tables (e.g., `documents`, `document_embeddings`, etc.).

---

## Running the Project

1. **Start the FastAPI Server**  
   ```bash
   uvicorn app.main:app --reload
   ```
   - The server will be available at [http://localhost:8000](http://localhost:8000).  
   - Interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs).

2. **(Optional) Start the React Frontend**  
   If you have the `frontend/` folder configured:
   ```bash
   cd frontend
   npm install
   npm start
   ```
   Your React app should be live at [http://localhost:3000](http://localhost:3000).

---

## Usage Guide

1. **Upload a Document**  
   - Endpoint: `POST /api/v1/documents/upload/`  
   - Form-data Fields:
     - **file**: The file you want to upload (e.g., `.txt` or `.pdf`).    
   - You can test this in Swagger at [http://localhost:8000/docs](http://localhost:8000/docs).

2. **Ask a Query**  
   - Endpoint: `POST /api/v1/analysis/query/`  
   - JSON Body:
     ```json
     {
       "query_text": "What is my closing balance?"
     }
     ```
   - The system will:
     1. Create an embedding for your query.  
     2. Retrieve the top matching chunks from your **bank_statement** documents.  
     3. Use GPT to generate an answer.  

3. **Check the Database**  
   - `documents` table: Each row represents an uploaded file.  
   - `document_embeddings` table: Each row represents a chunk embedding.

---

## Example Queries

- **“What was my closing balance in January?”**  
- **“How many deposits over \$1,000?”**  
- **“List all utility bill payments.”**

Because we’re using RAG, the system will reference **only** the text in your uploaded docs.
