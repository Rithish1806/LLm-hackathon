import os
import csv
import json
import logging
from dotenv import load_dotenv

from embeddings import embed_text, build_resource_embedding_text
from database import get_supabase_client, get_data_csv_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("career_rag.ingest")

load_dotenv()


def run_ingestion():
    """
    Ingests resources from CSV, computes 384-dimensional embeddings,
    and inserts them into Supabase PostgreSQL or local cache.
    """
    csv_path = get_data_csv_path()
    if not os.path.exists(csv_path):
        logger.error(f"Cannot find resources file: {csv_path}")
        return

    logger.info(f"Reading resources from: {csv_path}")
    resources = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            resources.append(row)

    logger.info(f"Found {len(resources)} resources to process.")

    supabase = get_supabase_client()
    processed_count = 0
    records_with_embeddings = []

    # Check if precomputed embeddings exist
    cache_path = os.path.join(os.path.dirname(__file__), "..", "data", "resources_embedded.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if len(cached) == len(resources):
                    logger.info(f"Loaded {len(cached)} precomputed records from disk cache.")
                    records_with_embeddings = cached
        except Exception:
            records_with_embeddings = []

    if not records_with_embeddings:
        for r in resources:
            item = {
                "title": r.get("title", ""),
                "description": r.get("description", ""),
                "skill": r.get("skill", ""),
                "role": r.get("role", ""),
                "difficulty": r.get("difficulty", "Beginner"),
                "type": r.get("type", "Course"),
                "duration": r.get("duration", "10 hours"),
                "provider": r.get("provider", "Verified Provider"),
                "url": r.get("url", ""),
                "career_goal": r.get("career_goal", "Job"),
                "content": r.get("content", ""),
                "verified": r.get("verified", "true").lower() == "true",
            }
            text_to_embed = build_resource_embedding_text(item)
            item["embedding"] = embed_text(text_to_embed)
            records_with_embeddings.append(item)
            processed_count += 1
            if processed_count % 10 == 0 or processed_count == len(resources):
                logger.info(f"Generated embeddings for {processed_count}/{len(resources)} resources...")

    if supabase:
        logger.info("Pushing records to Supabase 'resources' table...")
        try:
            # Clear existing table content to prevent duplicate accumulation
            supabase.table("resources").delete().neq("id", 0).execute()
            
            # Batch insert in chunks
            batch_size = 10
            for i in range(0, len(records_with_embeddings), batch_size):
                chunk = records_with_embeddings[i:i + batch_size]
                # Remove id from dict if auto-increment primary key
                cleaned_chunk = [{k: v for k, v in row.items() if k != "id"} for row in chunk]
                supabase.table("resources").insert(cleaned_chunk).execute()
                logger.info(f"Inserted batch {i // batch_size + 1}/{(len(records_with_embeddings) + batch_size - 1) // batch_size} into Supabase")

            logger.info(f"Successfully synced {len(records_with_embeddings)} resources to Supabase pgvector database!")
        except Exception as e:
            logger.error(f"Error writing to Supabase: {e}")
    else:
        logger.info("Supabase credentials not active. Caching precomputed embeddings to local store...")
        with open(cache_path, "w", encoding="utf-8") as out:
            json.dump(records_with_embeddings, out, indent=2)
        logger.info(f"Saved {len(records_with_embeddings)} embedded records to {cache_path}")

    logger.info("Ingestion completed successfully.")


if __name__ == "__main__":
    run_ingestion()
