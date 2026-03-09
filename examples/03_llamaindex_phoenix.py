import os
import logging
from typing import List
import time

from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.openai import OpenAI

try:
    import phoenix as px
    from arize_phoenix.trace.langchain import PhoenixCallbackHandler
except ImportError:
    print("Install Arize Phoenix: pip install arize-phoenix")

from src.observability import instrument_openai
from src.eval_utils import evaluate_rag_with_ragas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

instrument_openai()

from llama_index.embeddings.openai import OpenAIEmbedding


def setup_phoenix():
    try:
        px.launch_app()
        logger.info("Phoenix app launched at http://localhost:6006")
        return True
    except Exception as e:
        logger.warning(f"Phoenix setup failed: {e}")
        return False


class LlamaIndexRAG:
    def __init__(self):
        self.phoenix_handler = PhoenixCallbackHandler()
        
        Settings.llm = OpenAI(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1
        )
        
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        documents = self._create_sample_documents()
        
        self.index = VectorStoreIndex.from_documents(
            documents,
            show_progress=True
        )
        
        logger.info(f"RAG index created with {len(documents)} documents")
    
    def _create_sample_documents(self) -> List[Document]:
        docs = [
            Document(
                text="RAG (Retrieval Augmented Generation) is a technique that combines "
                     "retrieval and generation. It retrieves relevant documents first, then "
                     "generates response based on the retrieved context.",
                metadata={"source": "rag_guide.md"}
            ),
            Document(
                text="LLMs can have hallucinations where they generate plausible-sounding "
                     "but false information. RAG mitigates this by grounding responses in "
                     "retrieved documents.",
                metadata={"source": "llm_limitations.md"}
            ),
            Document(
                text="Vector databases like Pinecone, Weaviate, and Milvus are used to "
                     "store and retrieve document embeddings efficiently.",
                metadata={"source": "vector_db_guide.md"}
            ),
            Document(
                text="Prompt engineering is critical for RAG quality. Good prompts should "
                     "clearly specify the task, context format, and expected output.",
                metadata={"source": "prompt_engineering.md"}
            ),
        ]
        return docs
    
    async def query(self, question: str, eval_enabled: bool = True) -> dict:
        start_time = time.time()
        
        query_engine = self.index.as_query_engine(
            similarity_top_k=3,
            callbacks=[self.phoenix_handler]
        )
        
        response = query_engine.query(question)
        
        contexts = [node.get_content() for node in response.source_nodes]
        answer = str(response)
        
        latency = time.time() - start_time
        
        result = {
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "latency_seconds": latency,
            "num_sources": len(contexts)
        }
        
        if eval_enabled:
            try:
                eval_scores = await evaluate_rag_with_ragas(
                    question=question,
                    answer=answer,
                    contexts=contexts
                )
                result["evaluation"] = eval_scores
                logger.info(f"RAGAS score: {eval_scores.get('ragas_score', 0):.2f}")
            except Exception as e:
                logger.warning(f"Evaluation failed: {e}")
                result["evaluation"] = None
        
        logger.info(f"Query processed in {latency:.2f}s")
        
        return result


async def monitor_for_drift(rag: LlamaIndexRAG, num_queries: int = 20):
    test_queries = [
        "What is RAG?",
        "How does RAG prevent hallucinations?",
        "What vector databases can be used?",
        "How do you write good prompts?",
        "What is the relationship between LLMs and RAG?",
        "Can RAG improve factuality?",
        "What are embeddings?",
        "How does semantic search work?",
    ]
    
    logger.info(f"Running {num_queries} queries for drift detection...")
    
    for i in range(num_queries):
        query = test_queries[i % len(test_queries)]
        result = await rag.query(query, eval_enabled=True)
        
        if (i + 1) % 5 == 0:
            logger.info(f"Processed {i+1}/{num_queries} queries")
    
    logger.info("Drift detection complete. Check Phoenix UI for insights:")
    logger.info("http://localhost:6006")


async def main():
    setup_phoenix()
    
    logger.info("Initializing LlamaIndex RAG...")
    rag = LlamaIndexRAG()
    
    test_queries = [
        "What is RAG and how does it work?",
        "Can RAG prevent hallucinations?",
        "What vector databases are available?",
    ]
    
    print("\n" + "="*70)
    print("LlamaIndex RAG with Phoenix Monitoring")
    print("="*70)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 70)
        
        result = await rag.query(query, eval_enabled=True)
        
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Sources: {result['num_sources']}")
        print(f"Latency: {result['latency_seconds']:.2f}s")
        
        if result.get("evaluation"):
            evals = result["evaluation"]
            print(f"RAGAS Score: {evals.get('ragas_score', 0):.2f}")
            print(f"Faithfulness: {evals.get('faithfulness', 0):.2f}")
            print(f"Answer Relevancy: {evals.get('answer_relevancy', 0):.2f}")
    
    print("\n" + "="*70)
    print("Running drift detection (20 queries)...")
    print("="*70)
    await monitor_for_drift(rag, num_queries=20)
    
    print("\n✅ Open Phoenix UI to see:")
    print("- Embedding drift visualization")
    print("- Token usage trends")
    print("- Retrieval quality metrics")
    print("- Response latency analysis")
    print("\nhttp://localhost:6006")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
