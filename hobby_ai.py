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
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY_2")
# TAVILY_API_KEY no longer needed — search is now via free/keyless DuckDuckGo (ddgs)

# 👇 FILE NAME MATRIX TARGET
ARCHIVE_FILE = "i hopefully pray this works.json"

CATEGORIES = ["gaming", "electronics", "engineering", "astrophysics", "cameras", "terminal ballistics", "external ballistics", "internal ballistics", "continuum mechanics", "penetration mechanics", "robotics", "psychology",
"quantum_computing", "aerodynamics", "molecular_biology", "cryptography", "metallurgy", "networking", "thermodynamics", "machine_learning", "fluid_dynamics", "organic_chemistry", "quantitative_finance", "optics",
"biomimetic_gaits", "servo_telemetry", "inverse_kinematics", "power_distribution","neurotransmitter_kinetics", "micro_expression_facs", "speech_prosody_analysis", "social_signaling_metrics",
"plasma_physics", "evolutionary_game_theory", "computational_neuroscience", "nanomaterial_engineering",
"chaos_theory", "genomic_editing", "hypersonic_thermodynamics", "high_frequency_trading"]

PROMPTS = {
"gaming": "Delta Force Hawk Ops video game patch notes weapon meta weapon tuning armor penetration damage values",
"electronics": "ESP32-WROOM-32 hardware datasheet registry configurations clock gating power limits",
"engineering": "Structural steel 4140 mechanical properties handbook tensile yield strength metrics dimensions",
"astrophysics": "Orbital mechanics vis-viva equation delta-v calculation trajectories planetary physics parameters",
"cameras": "Camera sensor pixel binning mathematics signal to noise ratio SNR formatting equations",
"terminal ballistics": "terminal ballistics projectile deformation cavity formation wounding criteria metrics",
"external ballistics": "external ballistics drag coefficient bullet drop wind drift trajectory calculation",
"internal ballistics": "internal ballistics chamber pressure peak propellant burn rate expansion ratio equations",
"continuum mechanics": "continuum mechanics stress tensor strain tensor constitutive equations material mechanics",
"penetration mechanics": "penetration mechanics recht ipson model hydrodynamic penetration depth armor velocity",
"robotics": "robotic arm kinematics denavit hartenberg parameters actuator torque equations ros control",
"psychology": "dsm-5 diagnostic criteria cognitive behavioral therapy protocols neuroplasticity neural pathways",
"quantum_computing": "quantum error correction surface code stabilizer generators phase flip threshold fault tolerant",
"aerodynamics": "naca airfoil lift drag coefficient reynolds number chord length aerodynamics equations",
"molecular_biology": "crispr cas9 gna sequencing rna polymerase transcription translation molecular pathway mechanisms",
"cryptography": "aes 256 rsa key generation curve25519 discrete logarithm cryptographic initialization vectors",
"metallurgy": "iron carbon phase diagram martensite austenite tempering heat treatment hardness ttt curves",
"networking": "tcp ip window size packet header layout border gateway protocol rtt latency equations",
"thermodynamics": "carnot cycle efficiency entropy enthalpy change gibbs free energy equations gas laws",
"machine_learning": "transformer architecture attention mechanism weights backpropagation gradient descent math equations",
"fluid_dynamics": "navier stokes equations bernoulli equation laminar turbulent viscosity fluid dynamics parameters",
"organic_chemistry": "electrophilic aromatic substitution reaction mechanism sn1 sn2 activation energy pathways",
"quantitative_finance": "black scholes option pricing model implied volatility stochastic calculus garch equations",
"optics": "snells law refraction index lensmaker equation focal length laser wavelength optics equations",
"biomimetic_gaits": "multilegged crawling gait crawl trot tripod wave gait duty factor phase sequence parameters",
"servo_telemetry": "serial bus servo protocol st3215 lx-224 torque stall current position feedback register mapping",
"inverse_kinematics": "3dof robotic leg geometric inverse kinematics trigonometry cofe coordinates angle calculation equations",
"power_distribution": "high current lithium polymer lipo battery continuous discharge burst rating step down buck regulator schematic efficiency",
"neurotransmitter_kinetics": "oxytocin dopamine bonding pathway receptors up regulation mirroring neurobiology affinity metrics",
"micro_expression_facs": "facial action coding system facs action units micro expressions emotional micro-leakage decoding parameters",
"speech_prosody_analysis": "vocal prosody pitch variance fundamental frequency speech accommodation attraction mimicry acoustic analysis",
"social_signaling_metrics": "honest signaling thin slices behavior pro-social nonverbal displays baseline comfort markers interpersonal synchronization",
"plasma_physics": "magnetohydrodynamics navier stokes maxwell equations magnetic confinement fusion lawson criterion tokamak parameters",
"evolutionary_game_theory": "nash equilibrium replicator dynamics hawk dove game tit for tat cooperation evolutionary matrix equations",
"computational_neuroscience": "hodgkin huxley model spiking neural network cable theory action potential voltage gate equations",
"nanomaterial_engineering": "carbon nanotubes graphene lattice thermal conductivity youngs modulus chemical vapor deposition configurations",
"chaos_theory": "lorenz attractor lyapunov exponent strange attractors phase space bifurcation non-linear differential equations",
"genomic_editing": "base editors prime editing cas12a off target mutations target sequence efficiency metrics genomic mapping",
"hypersonic_thermodynamics": "stagnation enthalpy bow shock wave boundary layer ionization re-entry heating mach equations",
"high_frequency_trading": "limit order book mechanics market micro-structure latency arbitrage stochastic point processes market impact equations"
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


def query_openrouter_for_log_entry(system_prompt, user_prompt, max_attempts=3):
    """
    Calls OpenRouter and retries (staying on openrouter/free, which re-rolls the
    underlying model each call) if the response looks like junk rather than a
    real answer. Returns the clean text, or None if every attempt came back junk.
    """
    for attempt in range(1, max_attempts + 1):
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


print(f"Hobby loop running. Target storage file: '{ARCHIVE_FILE}'")

MAX_LOOPS = 25
loop_count = 0
success_count = 0
failure_count = 0

while loop_count < MAX_LOOPS:
    try:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        loop_count += 1

        # 1️⃣ Dynamically rotate categories so your offline data remains structurally varied
        search_query, assigned_cat = determine_next_dynamic_topic()

        # 2️⃣ Grab search results + full-page context from DuckDuckGo (free, no key)
        print(f" [{current_time}] Processing Loop #{loop_count}/{MAX_LOOPS} for category: '{assigned_cat}'...")
        real_grounding_text, sources = fetch_real_world_context(search_query)

        if real_grounding_text == "Global data matrix reference retrieval timeout.":
            failure_count += 1
            print(f"❌ No usable research context for '{assigned_cat}', skipping OpenRouter call.\n")
            # A little extra courtesy delay after a failure, on top of the loop's own
            # rate-limit padding below, to go easier on DDG before the next query.
            time.sleep(8)
            continue

        # 3️⃣ Query OpenRouter to parse it down into clean data rows, retrying if the
        #    free router lands on a flaky model that returns junk instead of a real answer
        system_prompt = "You are a precise technical data formatting assistant. Your job is to extract real data numbers, real patch logs, and accurate engineering constants from the provided context into Markdown formats. You are strictly forbidden from inventing dummy numbers or placeholder variables."
        user_prompt = f"Using the verified raw context text below:\n---\n{real_grounding_text}\n---\nCompile a technical log entry block for: '{search_query}'. Extract real numbers, formulas, or game data points directly from the context. Do not generate fictional numbers."

        clean_fact = query_openrouter_for_log_entry(system_prompt, user_prompt)

        if clean_fact is None:
            failure_count += 1
            print(f"❌ OpenRouter kept returning junk/non-answers for '{assigned_cat}' after retries — skipping save.\n")
            continue

        # 4️⃣ Lock clean text database entries to local repository file, with sources for provenance
        save_to_offline_database(clean_fact, current_time, assigned_cat, sources)
        success_count += 1
        print(f"📁 Success! True {assigned_cat} metrics written to '{ARCHIVE_FILE}'.\n")

    except Exception as e:
        failure_count += 1
        print(f"Core processing loop issue: {e}. Cooldown sequence start.")
        time.sleep(10)

    # Rate-limit safety padding — DuckDuckGo bot-detection tends to fire earlier
    # than most real search APIs, especially from shared CI-runner IPs.
    time.sleep(12 + random.uniform(0, 5))

print(f"⏱️ Loop completed. Processed: {loop_count} | Success: {success_count} | Failed: {failure_count}")

# Fail the workflow loudly if most of the run produced nothing usable, instead of
# silently exiting 0 like before. Tune the threshold if a partial-failure run is fine for you.
if loop_count > 0 and failure_count / loop_count > 0.5:
    print("❌ More than half of this run's loops failed to produce real data. Failing the job.")
    sys.exit(1)
