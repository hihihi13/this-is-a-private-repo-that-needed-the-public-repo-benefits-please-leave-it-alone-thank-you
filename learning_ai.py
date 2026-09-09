import time
import random
import datetime
import requests
import os
import json
import sys

from ddgs import DDGS
import trafilatura

# ========================================================
# 🔒 SECURE KEY CODES
# ========================================================
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
# TAVILY_API_KEY no longer needed — search is now via free/keyless DuckDuckGo (ddgs)

# 👇 UNIFIED FILE TARGET
ARCHIVE_FILE = "i pray this works 3.json"

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


def fetch_real_world_context(search_query, max_results=5, max_retries=3):
    """
    Free, keyless web search via DuckDuckGo (ddgs), enriched with full-page text
    extraction (trafilatura) from the top couple of results, since DDG only gives
    titles + short snippets on its own — not enough for the OpenRouter step to
    reliably pull real numbers/formulas out of.

    Returns: (content_text, sources_list)
    """
    results = []
    for attempt in range(1, max_retries + 1):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(search_query, max_results=max_results))
        except Exception as e:
            print(f"⚠️ DuckDuckGo search error (attempt {attempt}/{max_retries}): {e}")
            results = []

        if results:
            break

        print(f"⚠️ DuckDuckGo returned zero results for '{search_query}' "
              f"(attempt {attempt}/{max_retries}) — likely rate-limited. Backing off.")
        time.sleep(5 + random.uniform(0, 3) + attempt * 3)

    if not results:
        print(f"❌ DuckDuckGo gave no usable results for '{search_query}' after {max_retries} attempts.")
        return "Global data matrix reference retrieval timeout.", []

    sources = []
    snippet_block = ""
    for r in results:
        title = r.get("title", "")
        url = r.get("href", "")
        body = r.get("body", "")
        snippet_block += f"### {title}\n{body}\nSource: {url}\n\n"
        if url:
            sources.append({"title": title, "url": url})

    # Enrich with full-page text from the top 2 results — snippets alone are too
    # thin for the OpenRouter extraction step to find real numbers/formulas in.
    enriched_block = ""
    for r in results[:2]:
        url = r.get("href")
        if not url:
            continue
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                extracted = trafilatura.extract(downloaded)
                if extracted:
                    enriched_block += f"\n\n--- Full text from {url} ---\n{extracted[:4000]}"
        except Exception as e:
            print(f"⚠️ Could not extract full text from {url}: {e}")

    full_context = (snippet_block + enriched_block).strip()
    if not full_context:
        return "Global data matrix reference retrieval timeout.", []

    return full_context, sources


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


def is_junk_response(text):
    """
    Detects non-answer output from OpenRouter's free-model router — e.g. a raw
    moderation-classifier verdict ("User Safety: safe") leaking into the response
    instead of the actual log entry. This isn't the topic being blocked — it's a
    flaky underlying free model that `openrouter/free` randomly routed to on that
    call. It happens on completely unrelated topics too (networking, engineering),
    which confirms it isn't content-based.
    """
    if not text or not text.strip():
        return True
    lowered = text.strip().lower()
    junk_markers = ["user safety: safe", "user safety:", "user safety"]
    if any(lowered == m or lowered.startswith(m) for m in junk_markers):
        return True
    # A genuine log entry is always much longer than this — anything this short
    # is almost certainly a non-answer rather than real formatted content.
    if len(text.strip()) < 40:
        return True
    return False


def query_openrouter_for_log_entry(system_prompt, user_prompt, max_attempts=2):
    """
    Calls OpenRouter and retries (staying on openrouter/free, which re-rolls the
    underlying model each call) if the response looks like junk rather than a
    real answer. Returns the clean text, or None if every attempt came back junk.

    Every attempt — including retries — increments the global OPENROUTER_CALLS_USED
    counter, since failed/junk attempts still count against the daily free-tier quota.
    """
    global OPENROUTER_CALLS_USED

    for attempt in range(1, max_attempts + 1):
        OPENROUTER_CALLS_USED += 1
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "openrouter/free",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            },
            timeout=30
        )
        response.raise_for_status()
        text = response.json()['choices'][0]['message']['content']

        if not is_junk_response(text):
            return text

        print(f"⚠️ OpenRouter returned a junk/non-answer response "
              f"(attempt {attempt}/{max_attempts}): {text[:80]!r} — retrying.")
        time.sleep(3)

    return None


print(f" Learning AI looping. Saving to: '{ARCHIVE_FILE}'")

# 👇 Upper ceiling on search loops — the real gate below is the OpenRouter call budget
MAX_LOOPS = 50

# 👇 OpenRouter's free tier (no credits purchased) caps at 50 requests/day, account-wide.
#    This script runs twice a day, so each run gets a slice of that — 20 here, ×2 runs
#    = 40/day, leaving a ~10-request buffer for retries, manual test runs, etc.
#    Tune this down further if you still see 429s, or up if you confirm you have headroom.
MAX_OPENROUTER_CALLS = 20
OPENROUTER_CALLS_USED = 0

loop_count = 0
success_count = 0
failure_count = 0

while loop_count < MAX_LOOPS:
    if OPENROUTER_CALLS_USED >= MAX_OPENROUTER_CALLS:
        print(f"🛑 Reached this run's OpenRouter budget ({MAX_OPENROUTER_CALLS} calls) — "
              f"stopping early to stay within the shared 50/day free-tier limit. "
              f"Processed {loop_count} loops, used {OPENROUTER_CALLS_USED} OpenRouter calls.")
        break

    try:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        loop_count += 1

        # 1️⃣ Dynamically change fields so the database builds an all-rounder memory base
        search_query, assigned_cat = determine_next_dynamic_topic()

        # 2️⃣ Grab search results + full-page context from DuckDuckGo (free, no key)
        print(f" [{current_time}] Processing Loop #{loop_count}/{MAX_LOOPS} for core branch: '{assigned_cat}'...")
        real_grounding_text, sources = fetch_real_world_context(search_query)

        if real_grounding_text == "Global data matrix reference retrieval timeout.":
            failure_count += 1
            print(f"❌ No usable research context for '{assigned_cat}', skipping OpenRouter call.\n")
            time.sleep(8)
            continue

        # 3️⃣ Query OpenRouter to parse it into beautiful, dense markdown tables and
        #    descriptions, retrying if the free router lands on a flaky model that
        #    returns junk instead of a real answer
        system_prompt = "You are a precise technical data formatting assistant. Your job is to extract real data numbers, verifiable patch adjustments, scientific constants, and academic rules from the provided context into Markdown formats. You are strictly forbidden from inventing dummy numbers or hallucinating records."
        user_prompt = f"Using the verified raw context text below:\n---\n{real_grounding_text}\n---\nCompile a technical log entry block for the topic: '{search_query}'. Extract real numbers, formulas, constants, or text matrices directly from the context. Do not generate fictional data."

        clean_fact = query_openrouter_for_log_entry(system_prompt, user_prompt)

        if clean_fact is None:
            failure_count += 1
            print(f"❌ OpenRouter kept returning junk/non-answers for '{assigned_cat}' after retries — skipping save.\n")
            continue

        # 4️⃣ Commit directly to your local database tracking file, with sources for provenance
        save_to_offline_database(clean_fact, current_time, assigned_cat, sources)
        success_count += 1
        print(f" Success! data chunk successfully locked into '{ARCHIVE_FILE}'.\n")

    except Exception as e:
        failure_count += 1
        print(f" processing loop issue: {e}. Initiating 15-second loop protection cooldown.")
        time.sleep(15)

    # Rate-limit safety padding — DuckDuckGo bot-detection tends to fire earlier
    # than most real search APIs, especially from shared CI-runner IPs.
    time.sleep(10 + random.uniform(0, 5))

print(f"⏱️ Daily quota loop run complete. Total processed: {loop_count} | Success: {success_count} | "
      f"Failed: {failure_count} | OpenRouter calls used: {OPENROUTER_CALLS_USED}/{MAX_OPENROUTER_CALLS}")

# Fail the workflow loudly if most of the run produced nothing usable, instead of
# silently exiting 0 like before. Tune the threshold if a partial-failure run is fine for you.
if loop_count > 0 and failure_count / loop_count > 0.5:
    print("❌ More than half of this run's loops failed to produce real data. Failing the job.")
    sys.exit(1)