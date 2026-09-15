import os
import time
import logging
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import (
    CareerRole,
    ResourceItem,
    SkillGapRequest,
    SkillGapResponse,
    JobDescriptionRequest,
    JobDescriptionAnalysisResponse,
    RecommendationRequest,
    RecommendationResponse,
    RoadmapPhase,
    EvaluationMetrics,
)
from database import get_all_resources, get_supabase_client
from retrieval import retrieve_ranked_resources
from rag import generate_grounded_advice
from eval import run_rag_evaluation

_env_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_file):
    load_dotenv(dotenv_path=_env_file)
else:
    load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("career_rag.main")

app = FastAPI(
    title="EMP-24: AI Career Resource Advisor API",
    description="Retrieval-Augmented Generation (RAG) backend for career resource recommendations",
    version="1.0.0",
)

# CORS middleware for React / Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Default in-memory career roles definition
DEFAULT_CAREER_ROLES = [
    CareerRole(
        id=1,
        role_name="Data Analyst",
        description="Analyzes structured data to uncover business trends and build dashboards.",
        required_skills=["SQL", "Excel", "Power BI", "Statistics", "Python", "Data Visualization"],
    ),
    CareerRole(
        id=2,
        role_name="Data Scientist",
        description="Applies statistical modeling, machine learning, and advanced algorithms to predictive problems.",
        required_skills=["Python", "Statistics", "Machine Learning", "SQL", "Data Visualization"],
    ),
    CareerRole(
        id=3,
        role_name="Software Developer",
        description="Designs, builds, tests, and maintains full-stack software systems and applications.",
        required_skills=["Python", "Java", "C++", "React", "Git/GitHub", "SQL"],
    ),
    CareerRole(
        id=4,
        role_name="Machine Learning Engineer",
        description="Develops and scales machine learning pipelines, models, and inference services.",
        required_skills=["Python", "Machine Learning", "Statistics", "Git/GitHub", "Cloud"],
    ),
    CareerRole(
        id=5,
        role_name="Business Analyst",
        description="Translates business goals into technical requirements and operational dashboards.",
        required_skills=["Excel", "Power BI", "Tableau", "Communication", "SQL"],
    ),
    CareerRole(
        id=6,
        role_name="Cloud Engineer",
        description="Architects, provisions, and oversees scalable and secure cloud infrastructure.",
        required_skills=["Cloud", "Git/GitHub", "Python", "Cybersecurity"],
    ),
    CareerRole(
        id=7,
        role_name="Cybersecurity Analyst",
        description="Safeguards networks, data assets, and software endpoints against security threats.",
        required_skills=["Cybersecurity", "Python", "Cloud", "Aptitude"],
    ),
]


@app.get("/api/health")
def health_check():
    """Returns the service health status and active configuration status."""
    supabase_configured = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))
    hf_configured = bool(os.getenv("HUGGINGFACE_API_KEY"))
    resources = get_all_resources()

    return {
        "status": "online",
        "service": "EMP-24 AI Career Resource Advisor",
        "supabase_configured": supabase_configured,
        "huggingface_configured": hf_configured,
        "verified_resources_count": len(resources),
        "timestamp": time.time(),
    }


@app.get("/api/roles", response_model=List[CareerRole])
def get_roles():
    """Returns standard career roles and their required skill sets."""
    return DEFAULT_CAREER_ROLES


@app.get("/api/resources", response_model=List[ResourceItem])
def get_resources():
    """Returns all verified resources from the curated knowledge base."""
    return get_all_resources()


@app.post("/api/skill-gap", response_model=SkillGapResponse)
def analyze_skill_gap(req: SkillGapRequest):
    """Compares user skills against target role required skills."""
    role_match = next((r for r in DEFAULT_CAREER_ROLES if r.role_name.lower() == req.target_role.lower()), None)
    if not role_match:
        required_skills = ["SQL", "Python", "Git/GitHub"]
    else:
        required_skills = role_match.required_skills

    normalized_user_skills = {s.strip().lower() for s in req.current_skills if s.strip()}

    known = []
    missing = []
    for req_skill in required_skills:
        if req_skill.lower() in normalized_user_skills:
            known.append(req_skill)
        else:
            missing.append(req_skill)

    coverage = round((len(known) / len(required_skills)) * 100, 1) if required_skills else 0.0

    return SkillGapResponse(
        target_role=req.target_role,
        known_skills=known,
        missing_skills=missing,
        coverage_percent=coverage,
    )


@app.post("/api/analyze-job-description", response_model=JobDescriptionAnalysisResponse)
def analyze_job_description(req: JobDescriptionRequest):
    """Extracts required skills from job description text and calculates gaps."""
    known_skill_catalog = [
        "SQL", "Excel", "Python", "Power BI", "Tableau", "Statistics",
        "Machine Learning", "Data Visualization", "Java", "C++", "React",
        "Git/GitHub", "Cloud", "Cybersecurity", "Communication", "Aptitude"
    ]

    jd_lower = req.job_description.lower()
    extracted = []
    for skill in known_skill_catalog:
        if skill.lower() in jd_lower:
            extracted.append(skill)

    if not extracted:
        extracted = ["Python", "SQL", "Git/GitHub"]

    normalized_user = {s.strip().lower() for s in req.current_skills if s.strip()}
    known = [s for s in extracted if s.lower() in normalized_user]
    missing = [s for s in extracted if s.lower() not in normalized_user]

    summary = (
        f"Detected {len(extracted)} key skills from the job description. "
        f"You already have {len(known)} skill(s), leaving {len(missing)} skill(s) to target."
    )

    return JobDescriptionAnalysisResponse(
        target_role=req.target_role,
        extracted_skills=extracted,
        known_skills=known,
        missing_skills=missing,
        summary=summary,
    )


@app.get("/api/evaluate", response_model=EvaluationMetrics)
def evaluate_rag_pipeline():
    """Runs the benchmark evaluation suite and returns Precision@K, Recall@K, Groundedness, and Latency."""
    return run_rag_evaluation(top_k=3)


@app.post("/api/recommend", response_model=RecommendationResponse)
def recommend_pipeline(req: RecommendationRequest):
    """
    End-to-end RAG Recommendation Pipeline:
    1. Skill gap identification (role or JD)
    2. Query embedding via all-MiniLM-L6-v2
    3. Vector search via pgvector / in-memory cosine similarity
    4. Multi-factor re-ranking with explainable evidence
    5. Anti-hallucination grounded LLM synthesis
    6. Progressive roadmap timeline assembly
    """
    start_time = time.time()

    # Step 1: Skill Gap Identification
    if req.job_description and len(req.job_description.strip()) > 20:
        jd_analysis = analyze_job_description(JobDescriptionRequest(
            target_role=req.target_role,
            current_skills=req.current_skills,
            job_description=req.job_description
        ))
        coverage = round((len(jd_analysis.known_skills) / max(len(jd_analysis.extracted_skills), 1)) * 100, 1)
        gap_result = SkillGapResponse(
            target_role=req.target_role,
            known_skills=jd_analysis.known_skills,
            missing_skills=jd_analysis.missing_skills,
            coverage_percent=coverage
        )
    else:
        gap_result = analyze_skill_gap(SkillGapRequest(
            target_role=req.target_role,
            current_skills=req.current_skills,
        ))

    # Step 2 & 3 & 4: Vector Retrieval & Multi-Factor Re-Ranking
    top_resources = retrieve_ranked_resources(
        target_role=req.target_role,
        current_level=req.current_level,
        career_goal=req.career_goal,
        gap_result=gap_result,
        job_description=req.job_description,
        top_k=req.top_k or 6
    )

    # Step 5: Grounded LLM Advice Generation
    personalized_summary = generate_grounded_advice(
        target_role=req.target_role,
        current_level=req.current_level,
        career_goal=req.career_goal,
        available_time=req.available_time,
        gap_result=gap_result,
        resources=top_resources
    )

    # Step 6: Progressive Roadmap Construction
    p1_skills = gap_result.missing_skills[:2] if gap_result.missing_skills else ["Foundations Review"]
    p2_skills = gap_result.missing_skills[2:4] if len(gap_result.missing_skills) > 2 else ["Applied Problem Solving"]
    p3_skills = ["Capstone Projects", "Interview Aptitude & Communication"]

    phases = [
        RoadmapPhase(
            phase="Phase 1",
            timeline="Month 1",
            focus_skills=p1_skills,
            description=f"Focus on core missing prerequisites: {', '.join(p1_skills)}.",
            resource_ids=[r.id for r in top_resources[:2]]
        ),
        RoadmapPhase(
            phase="Phase 2",
            timeline="Month 2",
            focus_skills=p2_skills,
            description=f"Deepen tooling proficiency and practical assignments in: {', '.join(p2_skills)}.",
            resource_ids=[r.id for r in top_resources[2:4]]
        ),
        RoadmapPhase(
            phase="Phase 3",
            timeline="Month 3",
            focus_skills=p3_skills,
            description="Comprehensive portfolio build-out, mock test cases, and placement readiness.",
            resource_ids=[r.id for r in top_resources[4:6]]
        )
    ]

    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    supabase_active = bool(get_supabase_client())
    retrieval_mode = "supabase_pgvector" if supabase_active else "hybrid_curated_vector_store"

    return RecommendationResponse(
        target_role=req.target_role,
        current_level=req.current_level,
        career_goal=req.career_goal,
        available_time=req.available_time,
        skill_gap=gap_result,
        resources=top_resources,
        roadmap=phases,
        personalized_summary=personalized_summary,
        is_grounded=True,
        retrieval_mode=retrieval_mode,
        latency_ms=elapsed_ms,
    )
