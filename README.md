# 📚 Book Management Agent – AI-Powered RAG Platform

## Overview
**Book Management Agent** is an **AI-powered backend platform** that combines **traditional book management** with **Retrieval-Augmented Generation (RAG)** to deliver intelligent search, summaries, and recommendations.

The system is designed for **enterprise and SaaS use cases**, providing secure user management, document handling, and scalable AI-driven insights.

---

## 🚀 Key Highlights
- AI-powered **semantic search & recommendations**
- **LLaMA 3–based summaries** for books and reviews
- Secure **JWT authentication & RBAC**
- Modular, scalable backend architecture
- Production-ready with **PostgreSQL + optional AWS S3**

---

## 🧩 Core Modules

### 📚 Book & Content Management
- CRUD for Books, Authors, Genres
- Foreign-key relationships with integrity checks
- Book reviews with ratings
- Auto-generated AI summaries
- Genre-based recommendations

### 🤖 Generative AI & RAG
- Semantic search using natural language
- Sentence-transformer embeddings
- Automatic re-indexing on content changes
- Cosine similarity–based retrieval

### 👥 User & Access Control
- JWT-based authentication
- Role-Based Access Control (RBAC)
- Admin-only user & role management
- Granular permissions (read/write/delete/admin)

### 📄 Document Management
- Upload, download, and delete documents
- Local file handling for development
- AWS S3 support for production environments

---

## 🏗️ High-Level Architecture

```
Client / UI
   ↓
FastAPI Backend
   ↓
PostgreSQL Database
   ↓
Embeddings Generator
   ↓
Vector Store (In-Memory)
   ↓
LLM (LLaMA 3 via OpenRouter)
```

---

## 🛠️ Technology Stack

### Backend
- Python 3.8+
- FastAPI
- SQLAlchemy (Async)
- PostgreSQL

### AI & RAG
- LLaMA 3 (OpenRouter)
- sentence-transformers
- Vector similarity (cosine)

### Security
- JWT Authentication
- SHA-256 password hashing
- Role-based authorization

### Storage
- Local filesystem (development)
- AWS S3 (production – optional)

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- OpenRouter API Key

### Installation Steps

```bash
git clone <repository-url>
cd book_mgmt_backend
pip install -r requirements.txt
```

### Environment Configuration

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

Access:
- API Base: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🔌 API Overview

### Functional Areas
- Authentication & Authorization
- Books, Authors, Genres
- Reviews & AI Summaries
- Semantic Search (RAG)
- User & Role Management
- Document Storage

---

## 🧪 Testing

Run the full test suite:

```bash
pytest tests/ -v
```

Or:

```bash
python useful_scripts/test_scripts/run_tests.py
```

## 📄 License
MIT License
