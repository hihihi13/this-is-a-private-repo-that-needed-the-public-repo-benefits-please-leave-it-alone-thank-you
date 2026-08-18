import time
import datetime
import requests
import os
from upstash_vector import Index

# ========================================================
# 🔒 SECURE KEY CODES (Reuses your existing GitHub vault secrets)
# ========================================================
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")  
UPSTASH_URL = os.environ.get("UPSTASH_URL")
UPSTASH_TOKEN = os.environ.get("UPSTASH_TOKEN")

# Connect to Free Cloud Database
index = Index(url=UPSTASH_URL, token=UPSTASH_TOKEN)

print("🎮🌌 Hobby AI Deep Research Core is ONLINE.")
print("Starting intensive 25-minute specialized research block...")

start_time = time.time()
max_runtime_seconds = 25 * 60  # 25 minutes
max_loop_per_session = 12
loop_count = 0

while (time.time() - start_time) < max_runtime_seconds:
    try:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        loop_count += 1
        
        # Force OpenRouter to target your exact list of advanced hobbies with extreme depth
        response = requests.post(
            url="https://openrouter.ai",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
                        json={
                "model": "openrouter/free",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are Hobby AI, an expert technical database core. You are strictly restricted to researching: 1) Advanced Gaming Metas (Delta Force weapons/tactics, Genshin team rotations, Call of Duty movement/recoil). 2) Astrophysics & Astronomy (orbital mechanics, stellar nucleosynthesis, cosmic radiation). 3) Coding & Electronics (Python/C++, ESP32 microcontrollers, custom desktop PC configurations, soldering temperature logs). 4) Art & Cameras (perspective drawing, sensor pixel-binning, aperture/shutter math). 5) Military Technology & Engineering (small arms mechanical functions, ballistics physics coefficients, composite tank armor composition, artillery trajectory math, and chemical combustion/explosive velocity metrics)."
                    },
                    {
                        "role": "user", 
                        "content": f"Generate an ultra-deep technical file log #{int(time.time())}. Pick one exact sub-topic from your allowed list. Provide actual data arrays, frame-data, mechanical cross-sections, coding scripts, or mathematical formulas. No surface-level descriptions allowed."
                    }
                ]
            }

        )
        
        learned_fact = response.json()['choices']['message']['content']
        print(f"[{current_time}] Loop #{loop_count} - Hobby AI gathered {len(learned_fact)} bytes of expert data.")

        # 💾 Uses 'hobby_dense_fact' prefix to keep this data separated from school data
        from upstash_vector import vector
       
        vector_id = f"hobby_dense_fact_{int(time.time())}_{loop_count}"
        mock_embedding = [0.1] * 1536
        
        index.upsert(vectors=[
            (vector_id, mock_embedding, {"fact": learned_fact, "timestamp": current_time, "category": "hobby"})
        ])
        
        print("💾 Expert matrix safely pushed to cloud storage.")

    except Exception as e:
        print(f"❌ Core glitch: {e}. Re-engaging in 30 seconds.")
        time.sleep(30)

    time.sleep(45)

print(f"⏱️ Session complete. Total expert logs processed: {loop_count}.")
