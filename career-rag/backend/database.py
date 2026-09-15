import os
import csv
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from models import ResourceItem, CareerRole
from embeddings import embed_text, build_resource_embedding_text

_env_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_file):
    load_dotenv(dotenv_path=_env_file)
else:
    load_dotenv()

logger = logging.getLogger("career_rag.database")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_supabase_client = None
_in_memory_catalog: List[Dict[str, Any]] = []
_in_memory_embeddings: List[List[float]] = []


def get_supabase_client():
    """Initializes and returns the Supabase client if configured."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if SUPABASE_URL and SUPABASE_KEY and "your-project" not in SUPABASE_URL:
        try:
            from supabase import create_client
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Connected to Supabase PostgreSQL database successfully.")
            return _supabase_client
        except Exception as e:
            logger.warning(f"Could not connect to Supabase ({e}). Operating in local hybrid store mode.")
            return None
    return None


def get_data_csv_path() -> str:
    """Returns absolute path to data/resources.csv."""
    return os.path.join(os.path.dirname(__file__), "..", "data", "resources.csv")


def load_local_resources_from_csv() -> List[Dict[str, Any]]:
    """Loads all records from resources.csv."""
    global _in_memory_catalog, _in_memory_embeddings
    if _in_memory_catalog:
        return _in_memory_catalog

    csv_path = get_data_csv_path()
    if not os.path.exists(csv_path):
        logger.error(f"Resources CSV not found at {csv_path}")
        return []

    items = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            item = {
                "id": int(row.get("id", idx + 1)),
                "title": row.get("title", ""),
                "description": row.get("description", ""),
                "skill": row.get("skill", ""),
                "role": row.get("role", ""),
                "difficulty": row.get("difficulty", "Beginner"),
                "type": row.get("type", "Course"),
                "duration": row.get("duration", "10 hours"),
                "provider": row.get("provider", "Verified Provider"),
                "url": row.get("url", ""),
                "career_goal": row.get("career_goal", "Job"),
                "content": row.get("content", ""),
                "verified": row.get("verified", "true").lower() == "true",
            }
            items.append(item)

    _in_memory_catalog = items
    logger.info(f"Loaded {len(_in_memory_catalog)} verified resources into local store.")
    return _in_memory_catalog


def get_in_memory_embeddings() -> List[List[float]]:
    """Caches or loads embeddings for the local resource catalog."""
    global _in_memory_embeddings
    if _in_memory_embeddings and len(_in_memory_embeddings) == len(_in_memory_catalog):
        return _in_memory_embeddings

    # Check for precomputed disk cache first
    cache_path = os.path.join(os.path.dirname(__file__), "..", "data", "resources_embedded.json")
    if os.path.exists(cache_path):
        try:
            import json
            with open(cache_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                vectors = [item["embedding"] for item in cached_data if "embedding" in item]
                if len(vectors) == len(load_local_resources_from_csv()):
                    _in_memory_embeddings = vectors
                    logger.info(f"Loaded {len(_in_memory_embeddings)} precomputed 384-dim embeddings from cache.")
                    return _in_memory_embeddings
        except Exception as e:
            logger.warning(f"Could not load precomputed embeddings ({e}). Falling back to computation.")

    catalog = load_local_resources_from_csv()
    embeddings = []
    for item in catalog:
        text = build_resource_embedding_text(item)
        embeddings.append(embed_text(text))
    _in_memory_embeddings = embeddings
    return _in_memory_embeddings


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculates cosine similarity between two float vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = sum(a * a for a in vec1) ** 0.5
    norm_b = sum(b * b for b in vec2) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def search_resources_vector(
    query_embedding: List[float],
    match_count: int = 10,
    filter_role: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Performs vector similarity search.
    Tries Supabase RPC match_resources first; if unconfigured, uses in-memory cosine similarity.
    """
    client = get_supabase_client()
    if client:
        # Try 4-param signature first, then fallback to 2-param signature
        data = None
        try:
            rpc_params = {
                "query_embedding": query_embedding,
                "match_threshold": 0.0,
                "match_count": match_count,
                "filter_role": filter_role if filter_role else None
            }
            response = client.rpc("match_resources", rpc_params).execute()
            data = response.data
        except Exception:
            try:
                # Compatible with ChatGPT 2-param function: (query_embedding, match_count)
                rpc_params_compact = {
                    "query_embedding": query_embedding,
                    "match_count": match_count
                }
                response = client.rpc("match_resources", rpc_params_compact).execute()
                data = response.data
            except Exception as e:
                logger.warning(f"Supabase RPC match_resources failed ({e}). Falling back to local vector search.")

        if data:
            if filter_role:
                filtered = [r for r in data if filter_role.lower() in (r.get("role") or "").lower()]
                return filtered if filtered else data
            return data

    # Local In-Memory Cosine Similarity Vector Search
    catalog = load_local_resources_from_csv()
    doc_vectors = get_in_memory_embeddings()

    scored_items = []
    for item, doc_vec in zip(catalog, doc_vectors):
        # Optional role filter
        if filter_role and filter_role.lower() not in item["role"].lower():
            continue

        sim = cosine_similarity(query_embedding, doc_vec)
        scored_copy = dict(item)
        scored_copy["similarity"] = round(sim, 4)
        scored_items.append(scored_copy)

    # Sort descending by similarity
    scored_items.sort(key=lambda x: x["similarity"], reverse=True)
    return scored_items[:match_count]


def get_all_resources() -> List[ResourceItem]:
    """Returns all verified resources from Supabase or local CSV."""
    client = get_supabase_client()
    if client:
        try:
            res = client.table("resources").select("*").execute()
            if res.data:
                return [ResourceItem(**r) for r in res.data]
        except Exception as e:
            logger.warning(f"Failed to fetch resources from Supabase: {e}")

    raw_items = load_local_resources_from_csv()
    return [ResourceItem(**item) for item in raw_items]
