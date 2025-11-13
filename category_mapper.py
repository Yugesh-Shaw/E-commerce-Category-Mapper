"""
E-commerce Category Mapper
Uses Qwen 2.5 32B (hosted on Google Colab) and semantic embeddings to map
internal product categories to standardized marketplace categories.

Author: Yugesh
"""

import os
import pandas as pd
import aiohttp
import asyncio
import logging
import ujson
import urllib.parse
from asyncio import Semaphore
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Setup logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Configuration
# TODO: Update these paths for your environment
file_path = r"C:\Users\yuges\OneDrive\Documents\Tesco\Category mapping templete.xlsx"
output_file = file_path.replace(".xlsx", "_Tesco.xlsx")
autosave_file = file_path.replace(".xlsx", "_Tesco_Mapped_autosave.xlsx")
log_file = os.path.join(os.path.dirname(file_path), "category_mapping_logs.txt")

# TODO: Update with your ngrok URL from Colab
API_URL = "https://izaiah-unnumerated-unavailingly.ngrok-free.dev/generate"

# Configuration parameters
TOP_N_MATCHES = 30  # Number of candidates to send to LLM
MAX_CONCURRENT_REQUESTS = 2  # Concurrent API calls
SIMILARITY_THRESHOLD = 0.85  # Minimum similarity for auto-accept
AUTOSAVE_INTERVAL = 10  # Save progress every N items


def normalize(text):
    """Normalize string for comparison by removing special chars and lowercasing."""
    return ''.join(e.lower() for e in text if e.isalnum() or e.isspace()).strip()


def load_allowed_categories(file_path):
    """Load allowed marketplace categories from Excel."""
    try:
        df = pd.read_excel(file_path, sheet_name="Categories")
        allowed_categories = df.apply(
            lambda row: " > ".join(row.dropna().astype(str)), axis=1
        ).tolist()
        allowed_normalized = {normalize(cat): cat for cat in allowed_categories}
        logging.info(f"✅ Loaded {len(allowed_categories)} allowed categories.")
        return allowed_categories, allowed_normalized
    except Exception as e:
        logging.error(f"❌ Error loading allowed categories: {e}")
        raise


def load_input_categories(file_path):
    """Load internal categories to be mapped."""
    try:
        df_input = pd.read_excel(file_path, sheet_name="Check")
        categories_to_map = df_input.iloc[:, 0].tolist()
        logging.info(f"✅ Loaded {len(categories_to_map)} internal categories.")
        return df_input, categories_to_map
    except Exception as e:
        logging.error(f"❌ Error reading input sheet: {e}")
        raise


def initialize_model(allowed_categories):
    """Load sentence transformer model and encode allowed categories."""
    logging.info("🧠 Encoding allowed categories using embeddings...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    allowed_embeddings = model.encode(allowed_categories, convert_to_tensor=True)
    return model, allowed_embeddings


def get_top_matches(input_text, model, allowed_embeddings, allowed_categories, top_n=TOP_N_MATCHES):
    """Get top-N most similar allowed categories using semantic search."""
    input_embedding = model.encode([input_text], convert_to_tensor=True)
    similarities = cosine_similarity(input_embedding, allowed_embeddings)[0]
    top_indices = np.argsort(similarities)[-top_n:][::-1]
    return [allowed_categories[i] for i in top_indices]


def build_prompt(category, top_allowed):
    """Build prompt for LLM to select best matching category."""
    formatted_categories = "\n".join(f"- {c}" for c in top_allowed)
    
    return (
        f"You are a product categorization assistant.\n"
        f"Choose the nth level and most relevant and accurate category **from the list below** "
        f"for the given internal product title.\n"
        f"Properly UNDERSTAND the BASIC product type in the given title and the entire category you are mapping to.\n"
        f"Give priority to allowed categories in ascending order while selecting the most relevant category.\n"
        f"⚠️ ONLY respond with **one** of the exact category values from the list.\n"
        f"Do not rephrase, invent, or copy the internal category.\n"
        f"No explanations or formatting – just the category string.\n\n"
        f"Only output the single most appropriate category string from the list – exactly as it appears.\n"
        f"◆ Do not explain. Do not think aloud. Do not add any extra text or punctuation.\n"
        f"\n\nInternal category: '{category}'\n\n"
        f"Allowed categories:\n{formatted_categories}"
    )


def trailing_segment_match(response, candidates, max_depth=3):
    """Match based on trailing segments of category hierarchy."""
    norm_resp = normalize(response)
    for depth in range(1, max_depth + 1):
        for cat in candidates:
            tail = " > ".join(cat.split(" > ")[-depth:])
            if normalize(tail) == norm_resp:
                return cat
    return None


async def process_category(session, category, index, model, allowed_embeddings, 
                          allowed_categories, allowed_normalized, semaphore, log_file):
    """Process a single category through the mapping pipeline."""
    
    # Skip empty entries
    if not isinstance(category, str) or category.strip() == "":
        logging.warning(f"⚠️ Skipping empty row {index + 1}")
        return "", ""

    # Get top matching categories using semantic search
    top_allowed = get_top_matches(category, model, allowed_embeddings, allowed_categories)

    # Log top matches for audit trail
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n\n### Row {index + 1} - Internal Category: '{category}'\n")
        f.write("\n".join(f"- {match}" for match in top_allowed))
        f.write("\n" + ("-" * 60))

    # Build prompt and encode for API
    prompt = build_prompt(category, top_allowed)
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"{API_URL}?prompt={encoded_prompt}"

    # Call API with rate limiting
    async with semaphore:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                result_json = await response.json()
                result_text = result_json.get("response", "").strip()

                # Clean up response text
                if "...done thinking." in result_text:
                    result_text = result_text.split("...done thinking.")[-1].strip()

                # ✅ Step 1: Try exact normalized match
                norm_result = normalize(result_text)
                if norm_result in allowed_normalized:
                    matched = allowed_normalized[norm_result]
                    logging.info(f"✅ Row {index + 1}: Exact match → '{matched}'")
                    return matched, ""

                # ✅ Step 2: Try trailing segment match
                matched_trail = trailing_segment_match(result_text, top_allowed)
                if matched_trail:
                    logging.info(f"✅ Row {index + 1}: Trailing match → '{matched_trail}'")
                    return matched_trail, ""

                # ✅ Step 3: Semantic similarity fallback
                result_emb = model.encode([result_text], convert_to_tensor=True)
                top_emb = model.encode(top_allowed, convert_to_tensor=True)
                similarities = cosine_similarity(result_emb, top_emb)[0]
                best_idx = int(np.argmax(similarities))
                best_score = similarities[best_idx]
                best_match = top_allowed[best_idx]

                if best_score >= SIMILARITY_THRESHOLD:
                    logging.info(
                        f"✅ Row {index + 1}: Semantic fallback → '{result_text}' → "
                        f"'{best_match}' (Similarity: {best_score:.2f})"
                    )
                    return best_match, "Check"

                # Final fallback: keep API output but flag for review
                logging.warning(
                    f"⚠️ Row {index + 1}: Low confidence, keeping API output '{result_text}'"
                )
                return result_text, "Check"

        except Exception as e:
            logging.error(f"❌ Error processing row {index + 1}: {e}")
            return "Error", "Check"


async def process_all(categories_to_map, df_input, model, allowed_embeddings,
                     allowed_categories, allowed_normalized, autosave_file, log_file):
    """Process all categories with async API calls."""
    mapped_categories = []
    check_flags = []
    semaphore = Semaphore(MAX_CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession() as session:
        for i, category in enumerate(categories_to_map):
            mapped, flag = await process_category(
                session, category, i, model, allowed_embeddings,
                allowed_categories, allowed_normalized, semaphore, log_file
            )
            mapped_categories.append(mapped)
            check_flags.append(flag)

            # Autosave progress periodically
            if (i + 1) % AUTOSAVE_INTERVAL == 0:
                try:
                    df_temp = df_input.copy()
                    df_temp["Mapped Category"] = mapped_categories + [""] * (
                        len(categories_to_map) - len(mapped_categories)
                    )
                    df_temp["Check"] = check_flags + [""] * (
                        len(categories_to_map) - len(check_flags)
                    )
                    df_temp.to_excel(autosave_file, index=False)
                    logging.info(f"💾 Autosaved at row {i + 1}: {autosave_file}")
                except Exception as e:
                    logging.warning(f"⚠️ Could not autosave at row {i + 1}: {e}")

    return mapped_categories, check_flags


def main():
    """Main execution function."""
    logging.info("🚀 Starting category mapping process...")

    # Load data
    allowed_categories, allowed_normalized = load_allowed_categories(file_path)
    df_input, categories_to_map = load_input_categories(file_path)

    # Initialize model
    model, allowed_embeddings = initialize_model(allowed_categories)

    # Process all categories
    mapped_categories, check_flags = asyncio.run(
        process_all(
            categories_to_map, df_input, model, allowed_embeddings,
            allowed_categories, allowed_normalized, autosave_file, log_file
        )
    )

    # Save final output
    df_input["Mapped Category"] = mapped_categories
    df_input["Check"] = check_flags

    try:
        df_input.to_excel(output_file, index=False)
        logging.info(f"✅ Final output saved to: {output_file}")
    except Exception as e:
        logging.error(f"❌ Error saving final output: {e}")
        raise

    # Summary statistics
    total = len(mapped_categories)
    errors = sum(1 for m in mapped_categories if m == "Error")
    needs_check = sum(1 for f in check_flags if f == "Check")
    success = total - errors - needs_check

    logging.info("🎉 Mapping complete!")
    logging.info(f"📊 Summary: {success} auto-mapped, {needs_check} need review, {errors} errors")


if __name__ == "__main__":
    main()
