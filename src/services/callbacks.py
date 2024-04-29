
from typing import Dict, List, Any
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import AsyncIterable
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult

class MyCustomHandler(BaseCallbackHandler):
    def __init__(self, queue) -> None:
        super().__init__()
        # we will be providing the streamer queue as an input
        self._queue = queue
        # defining the stop signal that needs to be added to the queue in
        # case of the last token
        self._stop_signal = None
    
    # On the arrival of the new token, we are adding the new token in the 
    # queue
    def on_llm_new_token(self, token, **kwargs) -> None:
        self._queue.put(token)

    # on the start or initialization, we just print or log a starting message
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        pass

    # On receiving the last token, we add the stop signal, which determines
    # the end of the generation
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        self._queue.put(self._stop_signal)
        
        
        
        
        
class ChainHandler(BaseCallbackHandler):
    def __init__(self) -> None:
        super().__init__()
        self._stop_signal = None
        
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Run when chain ends running."""
        # print(outputs)
        
        


    class RetrieverCallbackHandler(AsyncIteratorCallbackHandler):
        def __init__(self, streaming_callback_handler) -> None:
            super().__init__()
            self.streaming_callback_handler = streaming_callback_handler

        async def on_retriever_end(self, source_docs, *, run_id, parent_run_id, tags, **kwargs):
            source_docs_d = [{"page": doc.metadata["page"]}
                            for doc in source_docs] if source_docs else None

            xtra = {"source_documents": source_docs_d}
            self.streaming_callback_handler.queue.put_nowait(xtra)