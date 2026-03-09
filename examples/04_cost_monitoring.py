import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

import openai
from src.observability import CostTracker, instrument_openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

instrument_openai()


class CostMonitor:
    def __init__(self, budget_per_day: float = 100.0):
        self.budget_per_day = budget_per_day
        self.daily_costs = defaultdict(float)
        self.model_costs = defaultdict(float)
        self.requests = []
    
    def log_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int
    ):
        cost = CostTracker.calculate_cost(model, input_tokens, output_tokens)
        today = datetime.now().strftime("%Y-%m-%d")
        
        self.daily_costs[today] += cost
        self.model_costs[model] += cost
        
        self.requests.append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "latency_ms": latency_ms,
            "total_tokens": input_tokens + output_tokens
        })
        
        logger.info(f"Cost tracked: {model} - {CostTracker.format_cost(cost)}")
        
        if self.daily_costs[today] > self.budget_per_day:
            logger.warning(f"🚨 Daily budget exceeded! "
                          f"${self.daily_costs[today]:.2f} > ${self.budget_per_day:.2f}")
    
    def get_daily_total(self, date: Optional[str] = None) -> float:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.daily_costs[date]
    
    def get_model_breakdown(self) -> Dict[str, float]:
        return dict(self.model_costs)
    
    def get_hourly_trend(self, hours: int = 24) -> List[Dict]:
        now = datetime.now()
        hourly = defaultdict(float)
        
        for req in self.requests:
            req_time = datetime.fromisoformat(req["timestamp"])
            if (now - req_time).total_seconds() < hours * 3600:
                hour_key = req_time.strftime("%Y-%m-%d %H:00")
                hourly[hour_key] += req["cost"]
        
        return sorted([
            {"hour": k, "cost": v} for k, v in hourly.items()
        ])
    
    def get_stats(self) -> Dict:
        if not self.requests:
            return {}
        
        total_cost = sum(r["cost"] for r in self.requests)
        total_tokens = sum(r["total_tokens"] for r in self.requests)
        avg_cost_per_request = total_cost / len(self.requests) if self.requests else 0
        avg_latency_ms = sum(r["latency_ms"] for r in self.requests) / len(self.requests)
        
        return {
            "total_requests": len(self.requests),
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "average_cost_per_request": avg_cost_per_request,
            "average_latency_ms": avg_latency_ms,
            "cost_per_1k_tokens": (total_cost / (total_tokens / 1000)) if total_tokens > 0 else 0,
            "today_cost": self.get_daily_total(),
            "daily_budget": self.budget_per_day,
            "remaining_budget": self.budget_per_day - self.get_daily_total()
        }
    
    def export_report(self, filepath: str = "cost_report.json"):
        report = {
            "generated_at": datetime.now().isoformat(),
            "stats": self.get_stats(),
            "model_breakdown": self.get_model_breakdown(),
            "hourly_trend": self.get_hourly_trend(),
            "requests": self.requests
        }
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report exported to {filepath}")
        return report


class CostOptimizedLLM:
    def __init__(self, max_daily_budget: float = 100.0):
        self.monitor = CostMonitor(max_daily_budget)
    
    def call_openai(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> str:
        start = time.time()
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        latency_ms = int((time.time() - start) * 1000)
        
        input_tokens = response["usage"]["prompt_tokens"]
        output_tokens = response["usage"]["completion_tokens"]
        
        self.monitor.log_request(model, input_tokens, output_tokens, latency_ms)
        
        cost = CostTracker.calculate_cost(model, input_tokens, output_tokens)
        logger.info(f"✓ {model} - {input_tokens}in / {output_tokens}out "
                   f"- {CostTracker.format_cost(cost)} - {latency_ms}ms")
        
        return response["choices"][0]["message"]["content"]
    
    def choose_model(self, quality_needed: str = "medium") -> str:
        daily_remaining = self.monitor.budget_per_day - self.monitor.get_daily_total()
        budget_utilization = self.monitor.get_daily_total() / self.monitor.budget_per_day
        
        logger.info(f"Budget utilization: {budget_utilization*100:.1f}% "
                   f"({CostTracker.format_cost(daily_remaining)} remaining)")
        
        if budget_utilization > 0.9:
            logger.warning("⚠️ High budget utilization - switching to gpt-3.5-turbo")
            return "gpt-3.5-turbo"
        elif budget_utilization > 0.7:
            logger.warning("⚠️ Moderate budget utilization - using balanced model")
            return "gpt-4" if quality_needed == "high" else "gpt-3.5-turbo"
        else:
            if quality_needed == "high":
                return "gpt-4-turbo"
            elif quality_needed == "medium":
                return "gpt-4"
            else:
                return "gpt-3.5-turbo"
    
    def get_report(self) -> Dict:
        return self.monitor.get_stats()


async def example_cost_tracking():
    logger.info("=" * 70)
    logger.info("Cost Tracking Example")
    logger.info("=" * 70)
    
    llm = CostOptimizedLLM(max_daily_budget=50.0)
    
    test_prompts = [
        ("What is machine learning?", "gpt-3.5-turbo"),
        ("Explain quantum computing in detail", "gpt-4"),
        ("Write a Python function", "gpt-3.5-turbo"),
        ("Analyze this data scientifically", "gpt-4-turbo"),
    ]
    
    for prompt, model in test_prompts:
        logger.info(f"\nPrompt: {prompt[:50]}...")
        response = llm.call_openai(prompt, model=model)
        logger.info(f"Response: {response[:100]}...")
    
    logger.info("\n" + "=" * 70)
    logger.info("Cost Summary")
    logger.info("=" * 70)
    
    stats = llm.get_report()
    
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Total Cost: {CostTracker.format_cost(stats['total_cost'])}")
    print(f"Total Tokens: {stats['total_tokens']:,}")
    print(f"Avg Cost/Request: {CostTracker.format_cost(stats['average_cost_per_request'])}")
    print(f"Avg Latency: {stats['average_latency_ms']:.0f}ms")
    print(f"Cost per 1K Tokens: {CostTracker.format_cost(stats['cost_per_1k_tokens'])}")
    print(f"Today's Cost: {CostTracker.format_cost(stats['today_cost'])}")
    print(f"Remaining Budget: {CostTracker.format_cost(stats['remaining_budget'])}")
    
    llm.monitor.export_report()


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_cost_tracking())
