# 📚✨ Book Management Backend  
### 🤖 AI‑Powered RAG Platform for Intelligent Content Management

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-success?logo=fastapi" />
  <img src="https://img.shields.io/badge/AI-RAG%20Enabled-purple?logo=openai" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

---

## 🌟 Overview
**Book Management Backend** is an **AI‑powered backend platform** that blends **classic content management** with **Retrieval‑Augmented Generation (RAG)** to deliver **intelligent search, summaries, and recommendations**.

Designed for **enterprise, SaaS, and AI‑native applications**, the platform provides secure access control, modular architecture, and scalable AI orchestration.

---

## 🚀 Key Features
- 🔍 **Semantic Search & RAG‑based Retrieval**
- 🧠 **LLaMA‑3 powered AI summaries**
- 🔐 **JWT Authentication & RBAC**
- ⚙️ **Modular, scalable FastAPI architecture**
- 🗄️ **PostgreSQL with optional AWS S3 storage**
- 📈 **Production‑ready & cloud‑deployable**

---

## 🧩 Core Modules

### 📚 Book & Content Management
- CRUD for Books, Authors, Genres
- Relational integrity with FK constraints
- Ratings & reviews
- Auto‑generated AI summaries
- Genre‑based recommendations

### 🤖 Generative AI & RAG
- Natural language semantic search
- Sentence‑transformer embeddings
- Cosine similarity‑based retrieval
- Automatic re‑indexing on content updates

### 👥 User & Access Control
- JWT‑based authentication
- Role‑Based Access Control (RBAC)
- Admin‑only user & role management
- Fine‑grained permissions

### 📄 Document Management
- Upload, download, delete documents
- Local storage for development
- AWS S3 support for production

---

## 🏗️ High‑Level Architecture

```
Client / UI
   ↓
FastAPI Backend
   ↓
PostgreSQL
   ↓
Embedding Generator
   ↓
Vector Store
   ↓
LLM (LLaMA‑3 via OpenRouter)
```

---

## 🛠️ Tech Stack

### Backend
- 🐍 Python 3.8+
- ⚡ FastAPI
- 🧩 SQLAlchemy (Async)
- 🗄️ PostgreSQL

### AI & RAG
- 🤖 LLaMA‑3 (OpenRouter)
- 📐 sentence‑transformers
- 📊 Vector similarity (cosine)

### Security
- 🔐 JWT Authentication
- 🔑 SHA‑256 password hashing
- 🛡️ Role‑based authorization

### Storage
- 💾 Local filesystem (dev)
- ☁️ AWS S3 (optional – prod)

---

## ⚙️ Setup & Installation

### ✅ Prerequisites
- Python 3.8+
- PostgreSQL
- OpenRouter API Key

### 📥 Installation
```bash
git clone <repository-url>
cd book_mgmt_backend
pip install -r requirements.txt
```

### 🔐 Environment Variables
Create a `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=book_mgmt
DB_USER=your_user
DB_PASSWORD=your_password

OPENROUTER_API_KEY=your_openrouter_key

USE_S3=false
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
AWS_REGION=us-east-1
```

---

## ▶️ Running the Application

```bash
uvicorn app.main:app --reload
```

🔗 API Base: http://localhost:8000 
---

## 🔌 API Capabilities
- Authentication & Authorization
- Books, Authors, Genres
- Reviews & AI Summaries
- Semantic Search (RAG)
- User & Role Management
- Document Storage

---

## 🧪 Testing

```bash
pytest tests/ -v
```

or

```bash
python useful_scripts/test_scripts/run_tests.py
```

---

## 🛣️ Roadmap
- 🧠 Persistent vector DB (FAISS / Milvus)
- 🔀 Hybrid keyword + semantic search
- ⏱️ Background async indexing
- 🏢 Multi‑tenant SaaS support
- 📊 Observability & metrics

---

## 📄 License
MIT License © 2026
