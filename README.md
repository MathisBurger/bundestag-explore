# Bundestag Citizen RAG 🏛️🤖

An intelligent, citizen-centric information system for the semantic analysis of and research into plenary minutes of the German Bundestag.

The system combines structured metadata from the official DIP API (such as *proceedings (Vorgänge)*, *subject areas (Sachgebiete)*, and *initiatives*) with a powerful **hybrid search method** (Dense Semantic Vectors + BM25 Sparse Vectors) in a Qdrant vector database. This enables citizens to analyze complex political debates, party positions, and specific quotes accurately, lightning-fast, and traceably.

---

## ⚠️ Current Project Status: Work in Progress (WIP)

> **IMPORTANT NOTE:** This project is currently in an **active development phase (Work in Progress)**. The core architecture for data processing, metadata cleaning, and indexing is already stable. Features may change as development progresses. The user interface (Streamlit) and the LLM synthesis are currently undergoing final alignment and implementation.

---

## 💡 Key Features

* **Hierarchical Parent-Child Chunking:** To ensure extremely precise vector search, long speeches are broken down into small segments (~120 words). However, when a search match occurs, the entire context of the speech is passed to the LLM. This prevents hallucinations and ensures contextual depth.
* **Advanced Metadata Indexing:** By linking MongoDB and the Bundestag's DIP API, the search can be precisely filtered by *speaker*, *political party*, *legislative period*, *date*, and official bill titles (*proceedings*).
* **Hybrid Search (Dense + Lexical):** Combines dense embeddings (`BAAI/bge-small-en-v1.5`) for conceptual, meaning-based questions (e.g., "stance on social security") with `Qdrant/bm25` sparse vectors for exact keyword and quote verification in the German language.
* **Memory-Optimized Scaling:** By enabling Qdrant's `on_disk_payload` mode, large text contexts remain on disk and do not strain the RAM. This is perfectly designed for scaling to hundreds of documents.

---

## 🏗️ Planned Roadmap & Next Steps

- [x] **Phases 1 & 2:** Plenary minutes parser with automatic agenda item recognition (*TOPs*).
- [x] **Phase 3:** MongoDB infrastructure connection (`mongo.py`) and flat metadata transformation for complex proceedings data.
- [x] **Phase 4:** Qdrant schema optimization with dedicated keyword, datetime, and full-text search indexes.
- [ ] **Phase 5 (In Progress):** Implementation of the interactive Streamlit web interface for citizens.
- [ ] **Phase 6 (In Progress):** RAG synthesis and answer generation using local LLMs (Ollama) or the OpenAI API.