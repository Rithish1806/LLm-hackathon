import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from models import ResourceItem, SkillGapResponse
from embeddings import embed_text
from database import search_resources_vector, load_local_resources_from_csv

load_dotenv()
logger = logging.getLogger("career_rag.retrieval")

# Configurable ranking weights (Default to 50% semantic, 20% role, 10% skill, 10% diff, 10% goal)
WEIGHT_SEMANTIC = float(os.getenv("WEIGHT_SEMANTIC", "0.50"))
WEIGHT_ROLE = float(os.getenv("WEIGHT_ROLE", "0.20"))
WEIGHT_SKILL = float(os.getenv("WEIGHT_SKILL", "0.10"))
WEIGHT_DIFFICULTY = float(os.getenv("WEIGHT_DIFFICULTY", "0.10"))
WEIGHT_CAREER_GOAL = float(os.getenv("WEIGHT_CAREER_GOAL", "0.10"))


def build_query_string(
    target_role: str,
    current_level: str,
    career_goal: str,
    missing_skills: List[str],
    job_description: Optional[str] = None
) -> str:
    """Builds a rich semantic search query representing the student's learning needs."""
    skills_part = ", ".join(missing_skills) if missing_skills else "advanced skills"
    query = f"Career role: {target_role}. Need to learn: {skills_part}. Skill level: {current_level}. Goal: {career_goal}."
    if job_description:
        # Append excerpt from job description to enhance semantic retrieval
        query += f" Target Job Description: {job_description[:200]}."
    return query


def calculate_multi_factor_score(
    resource: Dict[str, Any],
    semantic_similarity: float,
    target_role: str,
    current_level: str,
    career_goal: str,
    gap_result: SkillGapResponse
) -> tuple[float, List[str]]:
    """
    Computes multi-factor score and builds transparent 'Why recommended' evidence points.
    Final Score = 50% semantic + 20% role + 10% skill + 10% diff + 10% goal
    """
    evidence = []

    # 1. Semantic Similarity Component (0 to 1)
    s_sem = max(0.0, min(1.0, semantic_similarity))
    evidence.append(f"Semantic relevance score: {round(s_sem * 100, 1)}%")

    # 2. Role Match Component
    res_role = resource.get("role", "").lower()
    t_role = target_role.lower()
    if t_role in res_role or res_role in t_role:
        s_role = 1.0
        evidence.append(f"Matches target career role: {target_role}")
    else:
        s_role = 0.2

    # 3. Skill Gap Coverage Component
    res_skill = resource.get("skill", "")
    if res_skill in gap_result.missing_skills:
        s_skill = 1.0
        evidence.append(f"Directly targets missing skill gap: {res_skill}")
    elif res_skill in gap_result.known_skills:
        s_skill = 0.4
        evidence.append(f"Deepens proficiency in known skill: {res_skill}")
    else:
        s_skill = 0.1

    # 4. Difficulty Level Match Component
    res_diff = resource.get("difficulty", "").lower()
    u_diff = current_level.lower()
    if res_diff == u_diff:
        s_diff = 1.0
        evidence.append(f"Matches current skill level: {current_level}")
    elif (u_diff == "beginner" and res_diff == "intermediate") or (u_diff == "intermediate" and res_diff == "advanced"):
        s_diff = 0.6
        evidence.append(f"Next-stage progression to {res_diff.capitalize()}")
    else:
        s_diff = 0.2

    # 5. Career Goal Component
    res_goal = resource.get("career_goal", "").lower()
    u_goal = career_goal.lower()
    if u_goal in res_goal or res_goal in u_goal:
        s_goal = 1.0
        evidence.append(f"Aligned with {career_goal} preparation")
    else:
        s_goal = 0.4

    # Weighted Sum Formula
    final_score = (
        (WEIGHT_SEMANTIC * s_sem) +
        (WEIGHT_ROLE * s_role) +
        (WEIGHT_SKILL * s_skill) +
        (WEIGHT_DIFFICULTY * s_diff) +
        (WEIGHT_CAREER_GOAL * s_goal)
    )

    return min(final_score, 1.0), evidence


def retrieve_ranked_resources(
    target_role: str,
    current_level: str,
    career_goal: str,
    gap_result: SkillGapResponse,
    job_description: Optional[str] = None,
    top_k: int = 6
) -> List[ResourceItem]:
    """
    Executes RAG retrieval:
    1. Query embedding
    2. Vector similarity candidate retrieval
    3. Multi-factor re-ranking
    4. Evidence generation
    """
    query_text = build_query_string(
        target_role=target_role,
        current_level=current_level,
        career_goal=career_goal,
        missing_skills=gap_result.missing_skills,
        job_description=job_description
    )

    query_vector = embed_text(query_text)

    # Retrieve candidate pool (fetch top 15 candidates before re-ranking)
    candidates = search_resources_vector(
        query_embedding=query_vector,
        match_count=15,
        filter_role=None
    )

    ranked_items: List[ResourceItem] = []
    for cand in candidates:
        sem_sim = cand.get("similarity", 0.70)
        final_score, evidence = calculate_multi_factor_score(
            resource=cand,
            semantic_similarity=sem_sim,
            target_role=target_role,
            current_level=current_level,
            career_goal=career_goal,
            gap_result=gap_result
        )

        item = ResourceItem(
            id=cand["id"],
            title=cand["title"],
            description=cand["description"],
            skill=cand["skill"],
            role=cand["role"],
            difficulty=cand["difficulty"],
            type=cand["type"],
            duration=cand["duration"],
            provider=cand["provider"],
            url=cand["url"],
            career_goal=cand["career_goal"],
            content=cand.get("content", ""),
            verified=cand.get("verified", True),
            match_score=round(final_score * 100, 1),
            semantic_similarity=round(sem_sim, 3),
            why_recommended=" • ".join(evidence),
            evidence=evidence
        )
        ranked_items.append(item)

    # Sort descending by match_score
    ranked_items.sort(key=lambda x: (x.match_score or 0.0), reverse=True)
    return ranked_items[:top_k]
