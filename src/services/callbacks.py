
from typing import Dict, List, Any
from uuid import UUID
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import AsyncIterable
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
import json


class RetrieverCallbackHandler(AsyncIteratorCallbackHandler):
    def __init__(self, streaming_callback_handler) -> None:
        super().__init__()
        self.streaming_callback_handler = streaming_callback_handler
        self._stop_signal = None

    async def on_retriever_end(self, source_docs, *, run_id, parent_run_id, tags, **kwargs):
        source_docs_d = [{"page": doc.metadata["page"]} for doc in source_docs] if source_docs else None
        xtra = {"source_documents": source_docs_d}
        print(xtra)
        self.streaming_callback_handler._queue.put(xtra)

    async def on_chain_end(self, outputs: Dict[str, Any], *, run_id: UUID, parent_run_id: UUID | None = None, tags: List[str] | None = None, **kwargs: Any) -> None:
        pass

class MyCustomHandler(BaseCallbackHandler):
    def __init__(self, queue) -> None:
        super().__init__()
        self._queue = queue
        self._stop_signal = None

    def on_llm_new_token(self, token, **kwargs) -> None:
        self._queue.put({'text': token})

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self._queue.put(self._stop_signal)


