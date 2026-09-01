from __future__ import annotations
from typing import Any, Dict, Optional

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import requests

# -------------------
# PDF retriever store (per thread)
# NOTE: these dicts are populated by `ingest_pdf` in langraph_rag_backend.py.
# They live here (rather than there) because `rag_tool` needs to read them
# directly, and Python dicts are mutable objects — importing them by name
# into the backend module means both modules share the same underlying dict,
# so writes made in one module are visible in the other.
# -------------------
_THREAD_RETRIEVERS: Dict[str, Any] = {}
_THREAD_METADATA: Dict[str, dict] = {}


def _get_retriever(thread_id: Optional[str]):
    """Fetch the retriever for a thread if available."""
    if thread_id and thread_id in _THREAD_RETRIEVERS:
        return _THREAD_RETRIEVERS[thread_id]
    return None


# -------------------
# Tools
# -------------------
search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}

        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result,
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    )
    r = requests.get(url)
    return r.json()


@tool
def rag_tool(query: str, thread_id: Optional[str] = None) -> dict:
    """
    Retrieve relevant information from the uploaded PDF for this chat thread.
    Always include the thread_id when calling this tool.
    """
    retriever = _get_retriever(thread_id)
    if retriever is None:
        return {
            "error": "No document indexed for this chat. Upload a PDF first.",
            "query": query,
        }

    result = retriever.invoke(query)
    context = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {
        "query": query,
        "context": context,
        "metadata": metadata,
        "source_file": _THREAD_METADATA.get(str(thread_id), {}).get("filename"),
    }


tools = [search_tool, get_stock_price, calculator, rag_tool]