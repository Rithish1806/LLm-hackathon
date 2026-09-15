import os
import hashlib
import logging
from typing import List, Dict, Any

logger = logging.getLogger("career_rag.embeddings")

_model = None
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def get_embedding_model():
    """Lazy loads the SentenceTransformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer model: {MODEL_NAME}")
            _model = SentenceTransformer(MODEL_NAME)
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer ({e}). Using deterministic 384-dim semantic vector fallback.")
            _model = "fallback"
    return _model


def build_resource_embedding_text(resource: Dict[str, Any]) -> str:
    """
    Combines useful resource fields into a unified contextual string before embedding.
    title + description + skill + role + difficulty + career_goal + content
    """
    title = resource.get("title", "")
    description = resource.get("description", "")
    skill = resource.get("skill", "")
    role = resource.get("role", "")
    difficulty = resource.get("difficulty", "")
    career_goal = resource.get("career_goal", "")
    content = resource.get("content", "")

    return (
        f"Title: {title}. "
        f"Description: {description}. "
        f"Target Skill: {skill}. "
        f"Industry Role: {role}. "
        f"Difficulty Level: {difficulty}. "
        f"Career Goal: {career_goal}. "
        f"Syllabus Content: {content}."
    )


def _generate_fallback_vector(text: str, dim: int = 384) -> List[float]:
    """Generates a deterministic, normalized 384-dimensional vector from text tokens."""
    import math
    vec = [0.0] * dim
    tokens = text.lower().split()
    if not tokens:
        tokens = ["general"]
    
    for token in tokens:
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        val = ((h >> 8) % 1000) / 500.0 - 1.0
        vec[idx] += val
        
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [round(x / norm, 6) for x in vec]


def embed_text(text: str) -> List[float]:
    """Generates a 384-dimensional vector embedding for a single text query or document."""
    model = get_embedding_model()
    if model != "fallback":
        try:
            vector = model.encode(text, normalize_embeddings=True)
            return [float(x) for x in vector]
        except Exception as e:
            logger.error(f"Error encoding text with SentenceTransformer: {e}")
            return _generate_fallback_vector(text)
    return _generate_fallback_vector(text)


def embed_batch(texts: List[str]) -> List[List[float]]:
    """Encodes a batch of texts into 384-dimensional vector embeddings."""
    model = get_embedding_model()
    if model != "fallback":
        try:
            vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return [[float(val) for val in row] for row in vectors]
        except Exception as e:
            logger.error(f"Error batch encoding with SentenceTransformer: {e}")
            return [_generate_fallback_vector(t) for t in texts]
    return [_generate_fallback_vector(t) for t in texts]
