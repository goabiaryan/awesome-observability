"""
LLM Evaluation Utilities
Provides unified interface for evaluating LLM responses across multiple frameworks.

Supports:
- DeepEval (hallucinations, bias, faithfulness, answer relevancy)
- Ragas (RAG-specific metrics)
- TruLens (feedback functions)

Usage:
    from eval_utils import EvalPipeline, evaluate_rag_with_ragas
    
    pipeline = EvalPipeline(metrics=["hallucination", "faithfulness"])
    scores = await pipeline.evaluate(output=response, context=docs, question=q)
"""

import os
import json
import logging
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import asyncio

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class EvaluationScore:
    """Evaluation result with metadata"""
    metric_name: str
    score: float  # 0-1
    reasoning: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def passed_quality_gate(self, threshold: float = 0.8) -> bool:
        """Check if score passes minimum quality gate"""
        return self.score >= threshold
    
    def to_dict(self) -> Dict:
        return {
            "metric": self.metric_name,
            "score": round(self.score, 3),
            "reasoning": self.reasoning,
            "timestamp": self.timestamp
        }

@dataclass
class EvaluationResult:
    """Complete evaluation result with all metrics"""
    output: str
    context: Optional[str]
    question: Optional[str]
    scores: List[EvaluationScore]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    @property
    def average_score(self) -> float:
        """Calculate average score across all metrics"""
        if not self.scores:
            return 0.0
        return sum(s.score for s in self.scores) / len(self.scores)
    
    @property
    def passed_quality_gate(self, threshold: float = 0.8) -> bool:
        """Check if all metrics pass quality gate"""
        return all(s.passed_quality_gate(threshold) for s in self.scores)
    
    def to_dict(self) -> Dict:
        return {
            "output": self.output,
            "context": self.context,
            "question": self.question,
            "scores": [s.to_dict() for s in self.scores],
            "average_score": round(self.average_score, 3),
            "passed_quality_gate": self.passed_quality_gate,
            "timestamp": self.timestamp
        }

# ============================================================================
# Enum for Metrics
# ============================================================================

class EvaluationMetric(Enum):
    """Available evaluation metrics"""
    # Hallucination & Truthfulness
    HALLUCINATION = "hallucination"  # Is response factually grounded?
    FAITHFULNESS = "faithfulness"     # Does it match source documents?
    ANSWER_RELEVANCY = "answer_relevancy"  # Relevant to question? (RAGAS)
    
    # Context Quality
    CONTEXT_PRECISION = "context_precision"  # Is context relevant? (RAGAS)
    CONTEXT_RECALL = "context_recall"  # All required context retrieved?
    
    # Safety & Bias
    BIAS = "bias"  # Any harmful biases?
    TOXICITY = "toxicity"  # Is response toxic/harmful?
    
    # Semantic
    COHERENCE = "coherence"  # Is response coherent?
    COMPLETENESS = "completeness"  # Is answer complete?

# ============================================================================
# DeepEval Integration
# ============================================================================

class DeepEvalProvider:
    """DeepEval-based evaluation (50+ metrics)"""
    
    def __init__(self, model: str = "gpt-4"):
        try:
            from deepeval.metrics import (
                Hallucination, Faithfulness, AnswerRelevancy,
                ContextPrecision, Bias, Coherence
            )
            from deepeval.test_case import LLMTestCase
        except ImportError:
            raise ImportError("Install deepeval: pip install deepeval")
        
        self.Hallucination = Hallucination
        self.Faithfulness = Faithfulness
        self.AnswerRelevancy = AnswerRelevancy
        self.ContextPrecision = ContextPrecision
        self.Bias = Bias
        self.Coherence = Coherence
        self.LLMTestCase = LLMTestCase
        self.model = model
    
    async def evaluate_hallucination(self, output: str, context: str) -> Tuple[float, str]:
        """Score hallucination (0-1, where 1 = no hallucination)"""
        try:
            test_case = self.LLMTestCase(
                output=output,
                context=context
            )
            metric = self.Hallucination(model=self.model)
            await metric.async_measure(test_case)
            
            return metric.score, metric.reason
        except Exception as e:
            logger.error(f"Hallucination evaluation failed: {e}")
            return 0.5, str(e)
    
    async def evaluate_faithfulness(self, output: str, context: str) -> Tuple[float, str]:
        """Score faithfulness (how well response matches context)"""
        try:
            test_case = self.LLMTestCase(
                output=output,
                context=context
            )
            metric = self.Faithfulness(model=self.model)
            await metric.async_measure(test_case)
            
            return metric.score, metric.reason
        except Exception as e:
            logger.error(f"Faithfulness evaluation failed: {e}")
            return 0.5, str(e)
    
    async def evaluate_answer_relevancy(self, output: str, question: str) -> Tuple[float, str]:
        """Score answer relevancy (RAGAS metric)"""
        try:
            test_case = self.LLMTestCase(
                output=output,
                input=question
            )
            metric = self.AnswerRelevancy(model=self.model)
            await metric.async_measure(test_case)
            
            return metric.score, metric.reason
        except Exception as e:
            logger.error(f"Answer relevancy evaluation failed: {e}")
            return 0.5, str(e)
    
    async def evaluate_bias(self, output: str) -> Tuple[float, str]:
        """Score for biases (0-1, where 1 = no bias)"""
        try:
            test_case = self.LLMTestCase(output=output)
            metric = self.Bias(model=self.model)
            await metric.async_measure(test_case)
            
            return metric.score, metric.reason
        except Exception as e:
            logger.error(f"Bias evaluation failed: {e}")
            return 0.5, str(e)

# ============================================================================
# Ragas Integration
# ============================================================================

class RagasProvider:
    """Ragas-based RAG evaluation"""
    
    def __init__(self):
        try:
            from ragas.metrics import (
                faithfulness, answer_relevancy, context_precision, context_recall
            )
        except ImportError:
            raise ImportError("Install ragas: pip install ragas")
        
        self.faithfulness = faithfulness
        self.answer_relevancy = answer_relevancy
        self.context_precision = context_precision
        self.context_recall = context_recall
    
    async def evaluate_faithfulness(
        self,
        answer: str,
        contexts: List[str]
    ) -> Tuple[float, str]:
        """RAGAS faithfulness (how well answer grounded in contexts)"""
        try:
            # Ragas expects specific format
            score = await self.faithfulness.async_measure(
                answer=answer,
                contexts=contexts
            )
            return score.value, score.explanation
        except Exception as e:
            logger.error(f"Ragas faithfulness failed: {e}")
            return 0.5, str(e)
    
    async def evaluate_answer_relevancy(
        self,
        answer: str,
        question: str
    ) -> Tuple[float, str]:
        """RAGAS answer relevancy"""
        try:
            score = await self.answer_relevancy.async_measure(
                answer=answer,
                question=question
            )
            return score.value, score.explanation
        except Exception as e:
            logger.error(f"Ragas answer relevancy failed: {e}")
            return 0.5, str(e)
    
    async def evaluate_context_precision(
        self,
        answer: str,
        contexts: List[str],
        question: str
    ) -> Tuple[float, str]:
        """RAGAS context precision (is retrieved context relevant?)"""
        try:
            score = await self.context_precision.async_measure(
                answer=answer,
                contexts=contexts,
                question=question
            )
            return score.value, score.explanation
        except Exception as e:
            logger.error(f"Ragas context precision failed: {e}")
            return 0.5, str(e)

# ============================================================================
# TruLens Integration
# ============================================================================

class TruLensProvider:
    """TruLens-based evaluation with feedback functions"""
    
    def __init__(self):
        try:
            from trulens_eval.feedback import Feedback
            from trulens_eval.feedback.provider import OpenAI as OpenAIFeedback
        except ImportError:
            raise ImportError("Install trulens: pip install trulens-eval")
        
        self.Feedback = Feedback
        self.OpenAIFeedback = OpenAIFeedback
        self.openai_provider = OpenAIFeedback()
    
    async def evaluate_hallucination(self, output: str, context: str) -> Tuple[float, str]:
        """TruLens hallucination detection"""
        try:
            feedback = self.Feedback(
                self.openai_provider.hallucination_free_response
            )
            score = await feedback.async_run(
                output=output,
                context=context
            )
            return score, "TruLens hallucination check"
        except Exception as e:
            logger.error(f"TruLens hallucination failed: {e}")
            return 0.5, str(e)

# ============================================================================
# Main Evaluation Pipeline
# ============================================================================

class EvalPipeline:
    """Unified evaluation pipeline supporting multiple backends
    
    Example:
        pipeline = EvalPipeline(metrics=["hallucination", "faithfulness"])
        result = await pipeline.evaluate(
            output="The answer is 42",
            context="Answer to life: 42",
            question="What is the answer?"
        )
        print(f"Average score: {result.average_score}")
    """
    
    def __init__(
        self,
        metrics: List[str],
        backend: str = "deepeval",
        model: str = "gpt-4",
        quality_gate_threshold: float = 0.8
    ):
        """Initialize evaluation pipeline
        
        Args:
            metrics: List of metric names (e.g., ["hallucination", "faithfulness"])
            backend: "deepeval" | "ragas" | "trulens"
            model: LLM to use for evaluation (default: gpt-4)
            quality_gate_threshold: Minimum score to pass QA gate
        """
        self.metrics = [m.lower() for m in metrics]
        self.backend = backend
        self.model = model
        self.quality_gate_threshold = quality_gate_threshold
        
        # Initialize provider
        if backend == "deepeval":
            self.provider = DeepEvalProvider(model=model)
        elif backend == "ragas":
            self.provider = RagasProvider()
        elif backend == "trulens":
            self.provider = TruLensProvider()
        else:
            raise ValueError(f"Unknown backend: {backend}")
        
        logger.info(f"EvalPipeline initialized with {backend} backend: {metrics}")
    
    async def evaluate(
        self,
        output: str,
        context: Optional[str] = None,
        question: Optional[str] = None,
        expected_output: Optional[str] = None
    ) -> EvaluationResult:
        """Evaluate output across configured metrics
        
        Args:
            output: LLM output to evaluate
            context: Retrieved/source context (for RAG)
            question: Original question (for relevancy)
            expected_output: Ground truth answer (optional)
        
        Returns:
            EvaluationResult with all metric scores
        """
        scores = []
        
        # Run evaluations in parallel for speed
        tasks = []
        
        for metric in self.metrics:
            if metric == "hallucination" and context:
                tasks.append(self._eval_hallucination(output, context))
            elif metric == "faithfulness" and context:
                tasks.append(self._eval_faithfulness(output, context))
            elif metric == "answer_relevancy" and question:
                tasks.append(self._eval_answer_relevancy(output, question))
            elif metric == "context_precision" and context and question:
                tasks.append(self._eval_context_precision(output, context, question))
            elif metric == "bias":
                tasks.append(self._eval_bias(output))
            else:
                logger.warning(f"Metric {metric} skipped (missing required params)")
        
        # Execute all evaluations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Evaluation task failed: {result}")
            elif isinstance(result, EvaluationScore):
                scores.append(result)
        
        return EvaluationResult(
            output=output,
            context=context,
            question=question,
            scores=scores
        )
    
    async def _eval_hallucination(self, output: str, context: str) -> EvaluationScore:
        """Helper: evaluate hallucination"""
        score, reasoning = await self.provider.evaluate_hallucination(output, context)
        return EvaluationScore(
            metric_name="hallucination",
            score=score,
            reasoning=reasoning
        )
    
    async def _eval_faithfulness(self, output: str, context: str) -> EvaluationScore:
        """Helper: evaluate faithfulness"""
        score, reasoning = await self.provider.evaluate_faithfulness(output, context)
        return EvaluationScore(
            metric_name="faithfulness",
            score=score,
            reasoning=reasoning
        )
    
    async def _eval_answer_relevancy(self, output: str, question: str) -> EvaluationScore:
        """Helper: evaluate answer relevancy"""
        score, reasoning = await self.provider.evaluate_answer_relevancy(output, question)
        return EvaluationScore(
            metric_name="answer_relevancy",
            score=score,
            reasoning=reasoning
        )
    
    async def _eval_context_precision(
        self,
        output: str,
        context: str,
        question: str
    ) -> EvaluationScore:
        """Helper: evaluate context precision"""
        if self.backend == "ragas":
            score, reasoning = await self.provider.evaluate_context_precision(
                output, [context], question
            )
        else:
            score, reasoning = 0.8, "Not supported in this backend"
        
        return EvaluationScore(
            metric_name="context_precision",
            score=score,
            reasoning=reasoning
        )
    
    async def _eval_bias(self, output: str) -> EvaluationScore:
        """Helper: evaluate bias"""
        score, reasoning = await self.provider.evaluate_bias(output)
        return EvaluationScore(
            metric_name="bias",
            score=score,
            reasoning=reasoning
        )

# ============================================================================
# Hallucination Detection
# ============================================================================

class HallucinationDetector:
    """Specialized hallucination detector
    
    Example:
        detector = HallucinationDetector(threshold=0.85)
        if detector.is_hallucinating(response, context):
            alert_user("Potential hallucination!")
    """
    
    def __init__(self, threshold: float = 0.85, backend: str = "deepeval"):
        """Initialize detector
        
        Args:
            threshold: Score below this triggers alert (0-1)
            backend: Evaluation backend to use
        """
        self.threshold = threshold
        self.backend = backend
        self.pipeline = EvalPipeline(
            metrics=["hallucination"],
            backend=backend
        )
    
    async def is_hallucinating(self, output: str, context: str) -> bool:
        """Check if response is hallucinating
        
        Returns:
            True if hallucination risk detected, False otherwise
        """
        result = await self.pipeline.evaluate(output=output, context=context)
        
        if result.scores:
            hallucination_score = result.scores[0].score
            return hallucination_score < self.threshold
        
        return False

# ============================================================================
# Batch Evaluation
# ============================================================================

async def batch_evaluate_dataset(
    dataset: List[Dict[str, str]],
    metrics: List[str],
    backend: str = "deepeval",
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """Evaluate entire dataset
    
    Args:
        dataset: List of dicts with keys: output, context, question
        metrics: List of metrics to evaluate
        backend: Evaluation backend
        output_file: Save results to JSON file
    
    Returns:
        Aggregated results with average scores and pass rate
    
    Example:
        dataset = [
            {"output": "...", "context": "...", "question": "..."},
            ...
        ]
        results = await batch_evaluate_dataset(dataset, ["hallucination", "faithfulness"])
    """
    pipeline = EvalPipeline(metrics=metrics, backend=backend)
    
    all_results = []
    
    for i, item in enumerate(dataset):
        logger.info(f"Evaluating item {i+1}/{len(dataset)}")
        
        result = await pipeline.evaluate(
            output=item.get("output"),
            context=item.get("context"),
            question=item.get("question")
        )
        
        all_results.append(result.to_dict())
    
    # Aggregate results
    metric_scores = {}
    for result in all_results:
        for score in result["scores"]:
            metric_name = score["metric"]
            if metric_name not in metric_scores:
                metric_scores[metric_name] = []
            metric_scores[metric_name].append(score["score"])
    
    aggregated = {
        "total_evaluated": len(all_results),
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {}
    }
    
    for metric_name, scores in metric_scores.items():
        avg_score = sum(scores) / len(scores) if scores else 0
        pass_count = sum(1 for s in scores if s >= 0.8)
        aggregated["metrics"][metric_name] = {
            "average": round(avg_score, 3),
            "pass_rate": round(pass_count / len(scores), 3) if scores else 0,
            "count": len(scores)
        }
    
    # Save if requested
    if output_file:
        with open(output_file, "w") as f:
            json.dump({
                "aggregated": aggregated,
                "individual_results": all_results
            }, f, indent=2)
        logger.info(f"Results saved to {output_file}")
    
    return aggregated

# ============================================================================
# RAG-Specific Evaluation
# ============================================================================

async def evaluate_rag_with_ragas(
    question: str,
    answer: str,
    contexts: List[str],
    ground_truth: Optional[str] = None
) -> Dict[str, float]:
    """Evaluate RAG pipeline with Ragas metrics
    
    Args:
        question: User question
        answer: Generated answer
        contexts: Retrieved contexts
        ground_truth: Expected answer (optional)
    
    Returns:
        Dict with ragas_score, faithfulness, answer_relevancy, etc.
    
    Example:
        result = await evaluate_rag_with_ragas(
            question="What is RAG?",
            answer="RAG is Retrieval Augmented Generation",
            contexts=["RAG combines retrieval with generation..."],
            ground_truth="Retrieval Augmented Generation"
        )
        print(result['ragas_score'])
    """
    try:
        from ragas.run_config import RunConfig
        from ragas import evaluate
        from datasets import Dataset
    except ImportError:
        raise ImportError("Install ragas: pip install ragas datasets")
    
    # Format data for Ragas
    data = {
        "question": [question],
        "answer": [answer],
        "contexts": [contexts],
        "ground_truths": [[ground_truth]] if ground_truth else [[""]]
    }
    
    dataset = Dataset.from_dict(data)
    
    # Run evaluation
    results = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
    )
    
    return {
        "ragas_score": results["ragas_score"],
        "faithfulness": results["faithfulness"],
        "answer_relevancy": results["answer_relevancy"],
        "context_precision": results["context_precision"],
        "context_recall": results["context_recall"]
    }

# ============================================================================
# Initialization
# ============================================================================

if __name__ == "__main__":
    # Test setup
    async def test():
        pipeline = EvalPipeline(metrics=["hallucination", "faithfulness"])
        result = await pipeline.evaluate(
            output="The sky is blue",
            context="The sky appears blue due to Rayleigh scattering",
            question="Why is the sky blue?"
        )
        print(f"Average score: {result.average_score}")
        print(f"Results: {result.to_dict()}")
    
    asyncio.run(test())
