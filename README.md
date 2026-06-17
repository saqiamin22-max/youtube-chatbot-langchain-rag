# YouTube Chatbot (LangChain + RAG)

An advanced, AI-powered Retrieval-Augmented Generation (RAG) application that enables users to have interactive, context-aware conversations with any YouTube video using its transcript. Built with an asynchronous UI design, this tool extracts video dialogue, indexes it into a high-performance vector store, and uses Mistral AI models to stream exact answers, saving hours of watching long video content.

## 🚀 Features
- **Automated Dialogue Extraction:** Seamlessly extracts transcripts using the `youtube-transcript-api` with fallback logic for non-English/default language tracks.
- **Robust URL Parsing:** Custom regex and endpoint parsing logic that instantly handles standard (`youtube.com/watch?v=...`) and shortened (`youtu.be/...`) YouTube links.
- **Semantic Text Chunking:** Utilizes LangChain's `RecursiveCharacterTextSplitter` to chunk raw text elegantly while preserving overlap context.
- **Local Vector Search Architecture:** Employs `MistralAIEmbeddings` (`mistral-embed`) and packages text data into a local `FAISS` vector database for high-accuracy similarity searches.
- **LCEL Pipeline Integration:** Built cleanly using the LangChain Expression Language (LCEL) chain structure with streaming-first capabilities (`chain.stream()`).
- **Premium Custom UI:** A fully tailored Streamlit layout sporting fluid neon-dark CSS styling, sidebar-loaded video thumbnails, dynamic status badges, and asynchronous typing states.

## 🧱 Architecture Split
- `backend.py`: Contains the transcript ingestion engine, parsing logic, vector database pipeline, and the LCEL execution chain config.
- `app.py` (Frontend): Manages stateful persistence (`st.session_state`), sidebar setups, interactive chat history layouts, and custom UI style modifications.

## 🛠️ Tech Stack
- **Language:** Python
- **LLM & Vectors:** Mistral AI (`mistral-large-latest`, `mistral-embed`)
- **Frameworks:** LangChain Core, LangChain Community, LangChain MistralAI
- **Vector Storage:** FAISS
- **Frontend Layer:** Streamlit (with embedded HTML/CSS)
- **Data Scraping:** YouTube Transcript API

## 📦 How to Run

### 1. Clone the Repository
```bash
git clone [https://github.com/saqiamin22-max/YOUR_REPO_NAME.git](https://github.com/saqiamin22-max/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME
