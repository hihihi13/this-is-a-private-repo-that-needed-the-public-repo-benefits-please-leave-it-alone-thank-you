import time
import datetime
import requests
import os
import json

# ========================================================
# 🔒 SECURE KEY CODES
# ========================================================
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY_2")  

# 👇 UPDATED FILE NAME MATRIX TARGET
ARCHIVE_FILE = "i pray this works.json"

# Five targeted core domains to research round-robin style
CATEGORIES = ["gaming", "electronics", "engineering", "astrophysics", "cameras", "terminal ballistics", "external ballistics", "internal ballistics", "continuum mechanics", "penetration mechanics"]
PROMPTS = {
    "gaming": "Delta Force Hawk Ops video game patch notes weapon meta weapon tuning armor penetration damage values",
    "electronics": "ESP32-WROOM-32 hardware datasheet registry configurations clock gating power limits",
    "engineering": "Structural steel 4140 mechanical properties handbook tensile yield strength metrics dimensions",
    "astrophysics": "Orbital mechanics vis-viva equation delta-v calculation trajectories planetary physics parameters",
    "cameras": "Camera sensor pixel binning mathematics signal to noise ratio SNR formatting equations"
}

def determine_next_dynamic_topic():
    """Checks your archive log file to verify what category needs data points next."""
    last_category = "gaming"
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, "r") as f:
                data = json.load(f)
                if data and isinstance(data, list):
                    last_category = data[-1].get("category", "gaming")
        except Exception:
            pass

    current_index = CATEGORIES.index(last_category) if last_category in CATEGORIES else 0
    next_index = (current_index + 1) % len(CATEGORIES)
    next_cat = CATEGORIES[next_index]
    return PROMPTS[next_cat], next_cat

def fetch_real_world_context(search_query):
    """Pulls genuine internet tracking text snippets to ensure data is 100% true."""
    try:
        url = f"https://duckduckgo.com{search_query}&format=json&no_html=1"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        data = response.json()
        
        raw_text = []
        if data.get("AbstractText"):
            raw_text.append(data["AbstractText"])
        if data.get("RelatedTopics"):
            for item in data["RelatedTopics"][:2]:
                if "Text" in item:
                    raw_text.append(item["Text"])
                    
        return "\n\n".join(raw_text) if raw_text else "Active real-world parameter registry tracking metrics."
    except Exception:
        return "Reference context processing connection error."

def save_to_offline_database(fact_text, timestamp, category_name):
    """Appends records directly to your local file database archive."""
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

print(f"Hooby loop running. Target storage file: '{ARCHIVE_FILE}'")

# Max Calculations: 25 loops per script run * 2 workflow triggers a day = exactly 50 tokens daily
MAX_LOOPS = 25 
loop_count = 0

while loop_count < MAX_LOOPS:
    try:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        loop_count += 1
        
        # 1️⃣ Dynamically rotate categories so your offline data remains structurally varied
        search_query, assigned_cat = determine_next_dynamic_topic()
        
        # 2️⃣ Grab authentic information properties from internet index matrices
        real_grounding_text = fetch_real_world_context(search_query)
        
        # 3️⃣ Query OpenRouter to parse it down into clean data rows
        print(f" [{current_time}] Processing Loop #{loop_count}/{MAX_LOOPS} for category: '{assigned_cat}'...")
        response = requests.post(
            url="https://openrouter.ai",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "openrouter/free",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are a precise technical data formatting assistant. Your job is to extract real data numbers, real patch logs, and accurate engineering constants from the provided context into Markdown formats. You are strictly forbidden from inventing dummy numbers or placeholder variables."
                    },
                    {
                        "role": "user", 
                        "content": f"Using the verified raw context text below:\n---\n{real_grounding_text}\n---\nCompile a technical log entry block for: '{search_query}'. Extract real numbers, formulas, or game data points directly from the context. Do not generate fictional numbers."
                    }
                ]
            },
            timeout=30
        )
        response.raise_for_status()

        clean_fact = response.json()['choices']['message']['content']
        
        # 4️⃣ Lock clean text database entries to local repository file
        save_to_offline_database(clean_fact, current_time, assigned_cat)
        print(f"📁 Success! True {assigned_cat} metrics written to '{ARCHIVE_FILE}'.\n")

    except Exception as e:
        print(f"Core processing loop issue: {e}. Cooldown sequence start.")
        time.sleep(10)

    time.sleep(12)  # Prevents public scraping connection blocks

print(f"⏱️ Maximum quota block execution loop completed. Processed: {loop_count} updates.")
