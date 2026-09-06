import time
import datetime
import requests
import os
import json
import sys

# ========================================================
# 🔒 SECURE KEY CODES
# ========================================================
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")  # Added Tavily environment key

# 👇 UPDATED UNIFIED FILE TARGET
ARCHIVE_FILE = "i pray this works 3.json"

# Generalist category domains to research round-robin style
CATEGORIES = ["academic", "advanced_tech", "gaming_core", "current_affairs"]

PROMPTS = {
    "academic": "high school calculus formulas physics laws history timelines academic syllabus guide",
    "advanced_tech": "machine learning architectures data engineering standards computer science documentation",
    "gaming_core": "esports tournaments live video game patch balance notes competitive meta strategy updates",
    "current_affairs": "major international space exploration scientific breakthroughs technology news live summaries"
}


def determine_next_dynamic_topic():
    """Reads the archive log to see what category it researched last and shifts to the next domain."""
    last_category = "academic"
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, "r") as f:
                data = json.load(f)
            if data and isinstance(data, list):
                last_category = data[-1].get("category", "academic")
        except Exception:
            pass

    current_index = CATEGORIES.index(last_category) if last_category in CATEGORIES else 0
    next_index = (current_index + 1) % len(CATEGORIES)
    next_cat = CATEGORIES[next_index]
    return PROMPTS[next_cat], next_cat


def fetch_real_world_context(search_query, max_wait=150, poll_every=5):
    """
    Uses Tavily's /research endpoint to get a synthesized research report on the topic,
    instead of raw search snippets. /research is ASYNC: submit a task, then poll for
    its result using the request_id it hands back.

    Returns: (content_text, sources_list)
    """
    if not TAVILY_API_KEY:
        print("⚠️ Warning: TAVILY_API_KEY environment variable is missing.")
        return "Tavily API key is missing. Skipping external matrix lookup context.", []

    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }

    # 1) Submit the research task
    try:
        submit_response = requests.post(
            "https://api.tavily.com/research",
            headers=headers,
            json={
                "input": search_query,
                "model": "mini",          # "mini" = fast/narrow, matches our per-category prompts
                "output_length": "standard"
            },
            timeout=15
        )
        submit_response.raise_for_status()
        task = submit_response.json()
        request_id = task["request_id"]
    except Exception as e:
        print(f"⚠️ Web collection issue (submit stage): {e}")
        return "Global data matrix reference retrieval timeout.", []

    # 2) Poll until the task completes, fails, or we time out
    elapsed = 0
    while elapsed < max_wait:
        try:
            status_response = requests.get(
                f"https://api.tavily.com/research/{request_id}",
                headers=headers,
                timeout=15
            )
            status_response.raise_for_status()
            data = status_response.json()
        except Exception as e:
            print(f"⚠️ Web collection issue (poll stage): {e}")
            return "Global data matrix reference retrieval timeout.", []

        status = data.get("status")

        if status == "completed":
            content = data.get("content", "")
            sources = data.get("sources", [])
            if content:
                return content, sources
            return "Active global parameter verification block active.", []

        if status == "failed":
            print(f"⚠️ Tavily research task failed for query: '{search_query}'")
            return "Global data matrix reference retrieval timeout.", []

        # status is "pending" or "in_progress" — wait and check again
        time.sleep(poll_every)
        elapsed += poll_every

    print(f"⚠️ Tavily research task timed out after {max_wait}s for query: '{search_query}'")
    return "Global data matrix reference retrieval timeout.", []


def save_to_offline_database(fact_text, timestamp, category_name, sources):
    """Saves the factual, formatted database record directly to your local repository file."""
    existing_data = []
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, "r") as f:
                existing_data = json.load(f)
        except Exception:
            existing_data = []

    existing_data.append({
        "fact": fact_text,
        "timestamp": timestamp,
        "category": category_name,
        "sources": sources
    })

    with open(ARCHIVE_FILE, "w") as f:
        json.dump(existing_data, f, indent=4)


print(f" Learning AI looping. Saving to: '{ARCHIVE_FILE}'")

# 👇 MATCHES YOUR MAXIMUM DAILY API QUOTA
MAX_LOOPS = 50
loop_count = 0
success_count = 0
failure_count = 0

while loop_count < MAX_LOOPS:
    try:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        loop_count += 1

        # 1️⃣ Dynamically change fields so the database builds an all-rounder memory base
        search_query, assigned_cat = determine_next_dynamic_topic()

        # 2️⃣ Grab a synthesized research report + sources from Tavily
        print(f" [{current_time}] Processing Loop #{loop_count}/{MAX_LOOPS} for core branch: '{assigned_cat}'...")
        real_grounding_text, sources = fetch_real_world_context(search_query)

        if real_grounding_text in (
            "Global data matrix reference retrieval timeout.",
            "Tavily API key is missing. Skipping external matrix lookup context.",
            "Active global parameter verification block active."
        ):
            failure_count += 1
            print(f"❌ No usable research context for '{assigned_cat}', skipping OpenRouter call.\n")
            time.sleep(15)
            continue

        # 3️⃣ Query OpenRouter to parse it into beautiful, dense markdown tables and descriptions
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "openrouter/free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a precise technical data formatting assistant. Your job is to extract real data numbers, verifiable patch adjustments, scientific constants, and academic rules from the provided context into Markdown formats. You are strictly forbidden from inventing dummy numbers or hallucinating records."
                    },
                    {
                        "role": "user",
                        "content": f"Using the verified raw context text below:\n---\n{real_grounding_text}\n---\nCompile a technical log entry block for the topic: '{search_query}'. Extract real numbers, formulas, constants, or text matrices directly from the context. Do not generate fictional data."
                    }
                ]
            },
            timeout=30
        )
        response.raise_for_status()
        clean_fact = response.json()['choices'][0]['message']['content']

        # 4️⃣ Commit directly to your local database tracking file, with sources for provenance
        save_to_offline_database(clean_fact, current_time, assigned_cat, sources)
        success_count += 1
        print(f" Success! data chunk successfully locked into '{ARCHIVE_FILE}'.\n")

    except Exception as e:
        failure_count += 1
        print(f" processing loop issue: {e}. Initiating 15-second loop protection cooldown.")
        time.sleep(15)

    time.sleep(10)  # Rate-limit safety padding

print(f"⏱️ Daily quota loop run complete. Total processed: {loop_count} | Success: {success_count} | Failed: {failure_count}")

# Fail the workflow loudly if most of the run produced nothing usable, instead of
# silently exiting 0 like before. Tune the threshold if a partial-failure run is fine for you.
if loop_count > 0 and failure_count / loop_count > 0.5:
    print("❌ More than half of this run's loops failed to produce real data. Failing the job.")
    sys.exit(1)
