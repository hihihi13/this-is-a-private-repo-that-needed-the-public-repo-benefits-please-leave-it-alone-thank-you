import os
import time
import datetime
import requests
from upstash_vector import Index


OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")  
UPSTASH_URL = os.environ.get("UPSTASH_URL")
UPSTASH_TOKEN = os.environ.get("UPSTASH_TOKEN")

# Connect to Free Cloud Database
index = Index(url=UPSTASH_URL, token=UPSTASH_TOKEN)

print("⚡ Learning AI Maximum Efficiency Core is ONLINE.")
print("Starting intensive 25-minute automated research block...")

# Track time so we maximize our GitHub runtime without getting cut off (30-min hard limit)
start_time = time.time()
max_runtime_seconds = 25 * 60  # 25 minutes
max_loops_per_session = 14
loop_count = 0

while (time.time() - start_time) < max_runtime_seconds:
    try:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        loop_count += 1
        
        # 1. Force OpenRouter to generate massive, deep technical files
        response = requests.post(
            url="https://openrouter.ai",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
         json={
                "model": "openrouter/free",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are Learning AI, an advanced autonomous generalist data core with an omniscient, multi-disciplinary range of understanding. Your goal is to build an exhaustive master database that systematically covers all fields of human knowledge across all difficulty levels, blending foundational school academic syllabi, higher-education science/technology, live global current affairs, and comprehensive gaming knowledge (including game mechanics, esports strategies, competitive metas, design architectures, and industry updates)."
                    },
                    {
                        "role": "user", 
                        "content": f"Execute background research cycle #{int(time.time())}. Dynamically select a random topic from any field of knowledge at any difficulty level, or choose one of these primary domains to document with extreme depth: 1) ACADEMIC SYLLABUS: School math formulas, science concepts, or history guides. 2) ADVANCED TECH: Higher-level coding, engineering, or complex scientific theories. 3) GAMING CORE: Deep analysis of competitive mechanics, optimal strategy blueprints, patch updates, or esports meta shifts. 4) CURRENT AFFAIRS: Major global news or technological breakthroughs. Generate an exhaustive, high-density technical log with specific data."
                    }
                ]
            }


        )
        
        learned_fact = response.json()['choices']['message']['content']
        print(f"[{current_time}] Loop #{loop_count} - Learning AI gathered {len(learned_fact)} characters of high-density knowledge.")

        # 2. Upload straight to your Upstash Cloud Memory
        from upstash_vector import vector
        
        vector_id = f"dense_fact_{int(time.time())}_{loop_count}"
        mock_embedding = [0.1] * 1536
        
        index.upsert(vectors=[
            (vector_id, mock_embedding, {"fact": learned_fact, "timestamp": current_time})
        ])
        
        print("💾 High-density memory matrix safely pushed to Upstash cloud.")

    except Exception as e:
        print(f"❌ Core glitch: {e}. Cooling down for 30 seconds before re-engaging.")
        time.sleep(30)

    # Short delay between intense research cycles to prevent OpenRouter free-tier rate limits
    time.sleep(45)

print(f"⏱️ 25-Minute research block complete. Total dense matrices processed: {loop_count}. Powering down safely.")
