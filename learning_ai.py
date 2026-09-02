import time
import datetime
import requests
import os
import json

# ========================================================
# 🔒 SECURE KEY CODES 
# ========================================================
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")  
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")  # Added Tavily environment key

# 👇 UPDATED UNIFIED FILE TARGET
ARCHIVE_FILE = "i pray this works.json"

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

def fetch_real_world_context(search_query):
    """Queries live public index data via Tavily to prevent the AI model from fabricating facts."""
    if not TAVILY_API_KEY:
        return "Tavily API key is missing. Skipping external matrix lookup context."

    try:
        # Replaced old DuckDuckGo code block with standard Tavily POST request
        response = requests.post(
            "https://tavily.com",
            json={
                "api_key": TAVILY_API_KEY,
                "query": search_query,
                "search_depth": "basic",
                "max_results": 3
            },
            timeout=15
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        
        # Combine text content from search hits
        raw_context = [res["content"] for res in results if "content" in res]
        if raw_context:
            return "\n\n".join(raw_context)
            
        return "Active global parameter verification block active."
    except Exception:
        return "Global data matrix reference retrieval timeout."

def save_to_offline_database(fact_text, timestamp, category_name):
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
        "category": category_name
    })
    
    with open(ARCHIVE_FILE, "w") as f:
        json.dump(existing_data, f, indent=4)

print(f" Learning AI looping. Saving to: '{ARCHIVE_FILE}'")

# 👇 MATCHES YOUR MAXIMUM DAILY API QUOTA
# 50 loops per run * 1 run per day = exactly 50 tokens
MAX_LOOPS = 50 
loop_count = 0

while loop_count < MAX_LOOPS:
    try:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        loop_count += 1
        
        # 1️⃣ Dynamically change fields so the database builds an all-rounder memory base
        search_query, assigned_cat = determine_next_dynamic_topic()
        
        # 2️⃣ Scrape true reference snippets from public index layers
        real_grounding_text = fetch_real_world_context(search_query)
        
        # 3️⃣ Query OpenRouter to parse it into beautiful, dense markdown tables and descriptions
        print(f" [{current_time}] Processing Loop #{loop_count}/{MAX_LOOPS} for core branch: '{assigned_cat}'...")
        response = requests.post(
            url="https://openrouter.ai",
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
        
        # 4️⃣ Commit directly to your local database tracking file
        save_to_offline_database(clean_fact, current_time, assigned_cat)
        print(f" Success!  data chunk successfully locked into '{ARCHIVE_FILE}'.\n")

    except Exception as e:
        print(f" processing loop issue: {e}. Initiating 15-second loop protection cooldown.")
        time.sleep(15)

    time.sleep(10)  # Rate-limit safety padding

print(f"⏱️ Daily quota loop run complete. Total processed all-rounder entries: {loop_count}.")
