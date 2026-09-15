from typing import List, Optional
from pydantic import BaseModel, Field


class ResourceItem(BaseModel):
    id: int
    title: str
    description: str
    skill: str
    role: str
    difficulty: str
    type: str
    duration: str
    provider: str
    url: str
    career_goal: str
    content: Optional[str] = ""
    verified: bool = True
    match_score: Optional[float] = 0.0
    semantic_similarity: Optional[float] = 0.0
    why_recommended: Optional[str] = ""
    evidence: Optional[List[str]] = Field(default_factory=list)


class CareerRole(BaseModel):
    id: Optional[int] = None
    role_name: str
    description: str
    required_skills: List[str]


class SkillGapRequest(BaseModel):
    target_role: str
    current_skills: List[str]


class SkillGapResponse(BaseModel):
    target_role: str
    known_skills: List[str]
    missing_skills: List[str]
    coverage_percent: float


class JobDescriptionRequest(BaseModel):
    target_role: Optional[str] = None
    current_skills: List[str] = Field(default_factory=list)
    job_description: str


class JobDescriptionAnalysisResponse(BaseModel):
    target_role: Optional[str] = None
    extracted_skills: List[str]
    known_skills: List[str]
    missing_skills: List[str]
    summary: str


class RecommendationRequest(BaseModel):
    target_role: str
    current_level: str = "Beginner"
    current_skills: List[str] = Field(default_factory=list)
    career_goal: str = "Placement"
    available_time: str = "3 months"
    hours_per_week: Optional[int] = 10
    job_description: Optional[str] = None
    top_k: Optional[int] = 6


class RoadmapPhase(BaseModel):
    phase: str
    timeline: str
    focus_skills: List[str]
    description: str
    resource_ids: List[int] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    target_role: str
    current_level: str
    career_goal: str
    available_time: str
    skill_gap: SkillGapResponse
    resources: List[ResourceItem]
    roadmap: List[RoadmapPhase]
    personalized_summary: str
    is_grounded: bool
    retrieval_mode: str
    latency_ms: float


class EvaluationResultItem(BaseModel):
    query: str
    target_role: str
    retrieved_count: int
    precision_at_k: float
    recall_at_k: float
    groundedness_score: float
    latency_ms: float


class EvaluationMetrics(BaseModel):
    queries_tested: int
    mean_precision_at_k: float
    mean_recall_at_k: float
    mean_groundedness: float
    avg_latency_ms: float
    results: List[EvaluationResultItem]
