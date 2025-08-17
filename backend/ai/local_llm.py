"""
Local LLM adapter (lightweight stub)

This module provides a single async entrypoint `generate_local_response` that will:
- Use a real local LLM client if available (e.g. Ollama, Transformers) when installed.
- Otherwise return a safe stub response indicating local processing.

Replace the stub implementation with a real client integration when a local LLM is available.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("local_llm")

async def generate_local_response(user_input: str, context: Dict[str, Any], user_id: Optional[str] = None) -> str:
    """
    Generate a response using a local LLM if available.

    Args:
        user_input: sanitized user input string
        context: anonymized or original context dict
        user_id: optional user identifier

    Returns:
        A text response generated locally.
    """
    # Try to use Ollama (if installed). This is optional; keep fallback lightweight.
    try:
        # Ollama python client isn't a guaranteed dependency; import lazily.
        import ollama  # type: ignore

        # Example placeholder usage - adapt according to the actual client API
        # The real integration should include robust prompt templates, timeouts, and error handling.
        client = ollama.Ollama()
        prompt = f"User ({user_id}): {user_input}\nContext: {context}\nRespond concisely."
        result = client.create(prompt)  # placeholder API call
        return result.text if hasattr(result, "text") else str(result)
    except Exception:
        # Fallback stub response when no local LLM client is available
        await asyncio.sleep(0.05)  # simulate small processing delay
        stub = f"(local) Processed locally: {user_input[:500]}"
        logger.debug("Local LLM client not available - returning stub response")
        return stub
