import time
from typing import List, Dict, Any
from models import EvaluationMetrics, EvaluationResultItem, SkillGapResponse
from retrieval import retrieve_ranked_resources
from database import load_local_resources_from_csv

EVALUATION_DATASET = [
  {
    "query": "Beginner Data Analyst needs SQL and Excel for placement",
    "target_role": "Data Analyst",
    "current_level": "Beginner",
    "career_goal": "Placement",
    "relevant_skills": ["SQL", "Excel"],
  },
  {
    "query": "Software Developer switching to ML Engineer wants Python Statistics",
    "target_role": "Machine Learning Engineer",
    "current_level": "Intermediate",
    "career_goal": "Job",
    "relevant_skills": ["Machine Learning", "Statistics"],
  },
  {
    "query": "Cybersecurity Analyst starting from scratch with Linux and Networking",
    "target_role": "Cybersecurity Analyst",
    "current_level": "Beginner",
    "career_goal": "Job",
    "relevant_skills": ["Cybersecurity", "Cloud"],
  },
  {
    "query": "Business Analyst looking for Power BI and Tableau reporting",
    "target_role": "Business Analyst",
    "current_level": "Beginner",
    "career_goal": "Placement",
    "relevant_skills": ["Power BI", "Tableau"],
  }
]


def run_rag_evaluation(top_k: int = 3) -> EvaluationMetrics:
    """
    Executes automated RAG evaluation over curated benchmark queries.
    Measures Precision@K, Recall@K, Groundedness, and Latency.
    """
    catalog = load_local_resources_from_csv()
    valid_urls = {r["url"] for r in catalog}

    results: List[EvaluationResultItem] = []
    total_precision = 0.0
    total_recall = 0.0
    total_groundedness = 0.0
    total_latency = 0.0

    for test_case in EVALUATION_DATASET:
        t0 = time.time()

        gap = SkillGapResponse(
            target_role=test_case["target_role"],
            known_skills=[],
            missing_skills=test_case["relevant_skills"],
            coverage_percent=0.0
        )

        retrieved = retrieve_ranked_resources(
            target_role=test_case["target_role"],
            current_level=test_case["current_level"],
            career_goal=test_case["career_goal"],
            gap_result=gap,
            top_k=top_k
        )

        latency_ms = round((time.time() - t0) * 1000, 2)

        # Precision@K: proportion of retrieved resources matching at least one relevant skill or target role
        relevant_retrieved = 0
        grounded_count = 0
        retrieved_skills = set()

        for res in retrieved:
            # Check skill match
            if res.skill in test_case["relevant_skills"] or test_case["target_role"].lower() in res.role.lower():
                relevant_retrieved += 1
            retrieved_skills.add(res.skill)

            # Check grounding against authentic catalog
            if res.url in valid_urls:
                grounded_count += 1

        k = len(retrieved) or 1
        p_at_k = round(relevant_retrieved / k, 3)

        # Recall@K: proportion of relevant target skills covered in top-K
        matched_target_skills = [s for s in test_case["relevant_skills"] if s in retrieved_skills]
        r_at_k = round(len(matched_target_skills) / len(test_case["relevant_skills"]), 3) if test_case["relevant_skills"] else 1.0

        # Groundedness: proportion of resources that come from genuine verified knowledge base URLs
        groundedness = round(grounded_count / k, 3)

        total_precision += p_at_k
        total_recall += r_at_k
        total_groundedness += groundedness
        total_latency += latency_ms

        results.append(EvaluationResultItem(
            query=test_case["query"],
            target_role=test_case["target_role"],
            retrieved_count=len(retrieved),
            precision_at_k=p_at_k,
            recall_at_k=r_at_k,
            groundedness_score=groundedness,
            latency_ms=latency_ms
        ))

    n = len(EVALUATION_DATASET) or 1
    return EvaluationMetrics(
        queries_tested=n,
        mean_precision_at_k=round((total_precision / n) * 100, 1),
        mean_recall_at_k=round((total_recall / n) * 100, 1),
        mean_groundedness=round((total_groundedness / n) * 100, 1),
        avg_latency_ms=round(total_latency / n, 1),
        results=results
    )
