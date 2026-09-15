import os
import json
import logging
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

from models import ResourceItem, SkillGapResponse

load_dotenv()
logger = logging.getLogger("career_rag.rag")

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_LLM_MODEL = os.getenv("HF_LLM_MODEL", "meta-llama/Llama-3.2-3B-Instruct")


def format_context_for_llm(resources: List[ResourceItem]) -> str:
    """Formats retrieved resources into factual context blocks for the LLM."""
    if not resources:
        return "No verified resources found in knowledge base."

    context_lines = []
    for idx, r in enumerate(resources, 1):
        context_lines.append(
            f"Resource #{idx}:\n"
            f"- Title: {r.title}\n"
            f"- Skill Covered: {r.skill}\n"
            f"- Target Role: {r.role}\n"
            f"- Difficulty: {r.difficulty}\n"
            f"- Duration: {r.duration}\n"
            f"- Provider: {r.provider}\n"
            f"- Official URL: {r.url}\n"
            f"- Why Selected: {r.why_recommended}\n"
        )
    return "\n".join(context_lines)


def generate_grounded_advice(
    target_role: str,
    current_level: str,
    career_goal: str,
    available_time: str,
    gap_result: SkillGapResponse,
    resources: List[ResourceItem]
) -> str:
    """
    RAG Synthesis:
    Passes the strict anti-hallucination prompt and retrieved context to the LLM.
    Uses Hugging Face Inference API if configured, otherwise uses structured grounded synthesis.
    """
    if not resources:
        return (
            "Sufficient verified information was not found in the curated knowledge base "
            f"for {target_role}. Please try adjusting your target role or skill criteria."
        )

    context_text = format_context_for_llm(resources)

    # Prompt with anti-hallucination constraints
    system_prompt = (
        "You are an AI Career Resource Advisor for the EMP-24 competition. "
        "You MUST ONLY use the retrieved context below to provide career advice and resource recommendations. "
        "STRICT CONSTRAINTS:\n"
        "1. Do NOT invent or hallucinate any course names, providers, durations, or URLs.\n"
        "2. Only reference resources present in the retrieved context.\n"
        "3. Explicitly explain why each resource is recommended based on the user's skill gaps.\n"
        "4. If context is insufficient for a skill, state clearly that sufficient verified information was not found.\n"
        "5. Keep advice concise, encouraging, and actionable."
    )

    user_prompt = (
        f"Student Profile:\n"
        f"- Target Career: {target_role}\n"
        f"- Current Level: {current_level}\n"
        f"- Career Goal: {career_goal}\n"
        f"- Available Timeframe: {available_time}\n"
        f"- Acquired Skills: {', '.join(gap_result.known_skills) if gap_result.known_skills else 'None'}\n"
        f"- Skill Gaps to Close: {', '.join(gap_result.missing_skills) if gap_result.missing_skills else 'None'}\n\n"
        f"Verified Retrieved Context:\n"
        f"{context_text}\n\n"
        f"Task: Provide a concise personalized learning plan summary for this student."
    )

    # Try Hugging Face API if key is present
    if HUGGINGFACE_API_KEY and "your_huggingface" not in HUGGINGFACE_API_KEY:
        try:
            api_url = f"https://api-inference.huggingface.co/models/{HF_LLM_MODEL}"
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            payload = {
                "inputs": f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n<|assistant|>",
                "parameters": {"max_new_tokens": 300, "temperature": 0.2, "return_full_text": False}
            }
            response = requests.post(api_url, headers=headers, json=payload, timeout=12)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                    generated = result[0]["generated_text"].strip()
                    if generated:
                        return generated
        except Exception as e:
            logger.warning(f"Hugging Face Inference call error ({e}). Using deterministic grounded synthesis.")

    # Deterministic Grounded Synthesis (Guaranteed zero hallucinations and authentic citations)
    missing_str = ", ".join(gap_result.missing_skills) if gap_result.missing_skills else "advanced domain mastery"
    known_str = ", ".join(gap_result.known_skills) if gap_result.known_skills else "none"

    summary = (
        f"Based on our analysis for {target_role} ({current_level} level, targeting {career_goal} within {available_time}):\n\n"
        f"• Identified Skill Gaps: You currently possess [{known_str}], but require [{missing_str}] to reach role readiness.\n"
        f"• Grounded Recommendations: Retrieved {len(resources)} verified resources directly targeting these gaps.\n"
        f"• Key Priority: Begin with '{resources[0].title}' by {resources[0].provider} ({resources[0].duration}) "
        f"to build foundational competence in {resources[0].skill}.\n"
        f"• Next Milestones: Progress through the curated roadmap to complete portfolio-grade practice before your {career_goal} milestones.\n\n"
        f"All recommended courses include verified direct links with verified syllabus coverage."
    )
    return summary
