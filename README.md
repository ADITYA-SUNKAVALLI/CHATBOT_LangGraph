# Multi Utility RAG Chatbot

A multi-thread chatbot built with **LangGraph**, **Streamlit**, and **LangChain**, capable of:

- 📄 Answering questions about a PDF uploaded per chat (RAG, via a FAISS vector store + NVIDIA embeddings)
- 🌐 Web search (DuckDuckGo)
- 📈 Live stock price lookups (Alpha Vantage)
- 🧮 Basic arithmetic (calculator tool)
- 💬 Multiple independent chat threads, each with its own auto-generated title and its own attached PDF, persisted across restarts via a SQLite checkpointer

## Deployment

Deployment : https://chatbot-langgraph-zuz6.onrender.com

## Project Structure

```
.
├── chatbot.py            # Streamlit frontend (chat UI, sidebar, PDF upload)
├── chatbot_backend.py     # LangGraph graph, LLM setup, PDF ingestion, thread helpers
├── chatbot_tools.py       # Tool definitions: rag_tool, search_tool, calculator, get_stock_price
├── chatbot.db              # SQLite checkpoint store (auto-created at runtime, not committed)
├── requirements.txt
├── .env.example            # Template for required environment variables
└── .gitignore
```

## Prerequisites

- Python 3.10+
- An [OpenRouter](https://openrouter.ai/) API key (for the LLM)
- An [NVIDIA API](https://build.nvidia.com/) key (for embeddings)

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/ADITYA-SUNKAVALLI/CHATBOT_LangGraph
   cd CHATBOT_LangGraph

   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and fill in your keys:
   ```dotenv
   OPENROUTER_API_KEY=your_key_here
   NVIDIA_API_KEY=your_key_here
   ```
   LangSmith tracing (`LANGCHAIN_*` vars) is optional — leave `LANGCHAIN_TRACING_V2=false` if you don't use LangSmith.

5. **Run the app**
   ```bash
   streamlit run chatbot.py
   ```
   The app will open at `http://localhost:8501`.

## How it works

- Each browser session gets a `thread_id` (UUID). All messages for that thread are checkpointed to `chatbot.db` via LangGraph's `SqliteSaver`, so past conversations survive a restart.
- Uploading a PDF (via the 📎 button next to the chat input) builds a FAISS index scoped to that thread's `thread_id`; the `rag_tool` only searches the document attached to the current chat.
- The sidebar shows a short auto-generated title per chat (derived from the first reply) instead of the raw thread ID, plus a "New Chat" button to start a fresh thread.
- If the LLM provider returns a rate-limit / "too many requests" error mid-response, the UI shows a short countdown and asks you to retry rather than crashing.

## Notes on the model

The LLM is configured in `chatbot_backend.py`:
```python
llm = ChatOpenRouter(model="openrouter/free")
```
Free-tier OpenRouter models rotate and some don't reliably support tool calling — if you notice tool calls (`rag_tool`, `calculator`, etc.) not firing, swap in a model confirmed to support tools (e.g. `qwen/qwen3-coder:free`) and re-test.

