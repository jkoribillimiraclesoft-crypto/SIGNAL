import os
from anthropic import Anthropic
from database import Article

class IntelligenceEngine:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key) if api_key else None

    def calculate_relevance(self, raw_scores: dict, weights: dict) -> float:
        """Computes weighted score 0-100."""
        total_weight = sum(weights.values())
        if total_weight == 0: return 0
        weighted_sum = sum(raw_scores.get(k, 0) * weights.get(k, 0) for k in weights)
        return round(weighted_sum / total_weight, 1)

    def get_priority_label(self, score: float) -> str:
        if score >= 85: return "must"
        if score >= 70: return "important"
        if score >= 50: return "explore"
        return "watch"

    def analyze_trend(self, articles: list):
        """Simple trend analysis for the dashboard."""
        if not articles: return {}
        categories = [a.category for a in articles]
        return {cat: categories.count(cat) for cat in set(categories)}