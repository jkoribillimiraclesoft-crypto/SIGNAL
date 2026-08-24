from database import Article
from datetime import datetime

def seed_production_data(session, weights, intel_engine):
    raw_data = [
        {
            "title": "Vertex AI releases 'Grounding with Google Search' for Data Pipelines",
            "url": "https://gcp.blog/vertex-grounding",
            "source": "Google Cloud Blog",
            "category": "Vertex AI",
            "summary": "GCP engineers can now anchor LLM responses directly to Google Search results within BigQuery ML workflows.",
            "whats_new": "A new API parameter for Gemini models in Vertex AI enables real-time search grounding.",
            "why_matters": "Reduces hallucinations in automated data enrichment pipelines.",
            "why_learn": "Essential for building RAG applications on GCP.",
            "gcp_use": "Yes",
            "gcp_use_case": "Auto-verify corporate entities in your BigQuery tables using live web data.",
            "scores": {"gcp": 95, "de": 90, "ai": 85, "career": 90, "adoption": 70, "future": 80}
        },
        {
            "title": "Apache Beam adds native support for Hugging Face Transformers",
            "url": "https://beam.apache.org/hf-support",
            "source": "Apache Software Foundation",
            "category": "Dataflow",
            "summary": "Beam pipelines (Dataflow) can now load Hugging Face models natively for high-throughput batch inference.",
            "whats_new": "New RunInference transform specifically optimized for HF models.",
            "why_matters": "Makes deploying open-source models in GCP data pipelines much simpler.",
            "why_learn": "Key skill for any Data Engineer moving into LLMOps.",
            "gcp_use": "Yes",
            "gcp_use_case": "Process 10 million rows of sentiment analysis in Dataflow using a Llama-3 model.",
            "scores": {"gcp": 88, "de": 95, "ai": 80, "career": 85, "adoption": 75, "future": 70}
        }
    ]

    for item in raw_data:
        score = intel_engine.calculate_relevance(item['scores'], weights)
        priority = intel_engine.get_priority_label(score)
        
        article = Article(
            title=item['title'],
            url=item['url'],
            source=item['source'],
            category=item['category'],
            summary=item['summary'],
            whats_new=item['whats_new'],
            why_matters=item['why_matters'],
            why_learn=item['why_learn'],
            gcp_use=item['gcp_use'],
            gcp_use_case=item['gcp_use_case'],
            relevance_score=score,
            scores_json=item['scores'],
            priority=priority
        )
        session.add(article)
    session.commit()
