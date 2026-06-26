from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)


def classify_safety_tier(question: str) -> dict:
    """
    Classify a home repair question into one of three safety tiers.

    TODO — Milestone 1:

    Before writing any code, complete specs/classifier-spec.md. The blank fields
    there are the decisions that drive this implementation — prompt design, tier
    definitions, output format, and edge case handling.

    Your implementation should:
      1. Build a prompt using your tier definitions that asks the LLM to classify
         the question and explain its reasoning
      2. Send a single chat completion request (no tools, no history)
      3. Parse the tier and reason out of the raw response text
      4. Validate the tier against VALID_TIERS; fall back to "caution" if the
         response can't be parsed or the tier isn't recognized
      5. Return {"tier": ..., "reason": ...}

    Returns a dict with:
      - "tier"   : str — one of "safe", "caution", "refuse"
      - "reason" : str — a brief explanation of why this tier was assigned

    The three tiers:
      - "safe"    : routine, low-risk repairs most homeowners can handle safely
      - "caution" : doable with care, but mistakes have real cost or mild risk
      - "refuse"  : high-risk repairs that require a licensed professional —
                    mistakes can cause fire, flooding, injury, or structural damage
    """
    system_message = """
You are a safety classifier for a home repair assistant. Your job is to classify the user's repair question into exactly one tier: safe, caution, or refuse.

Tier definitions:
- safe: Routine DIY repairs that most homeowners can complete with basic tools, where mistakes usually cause only cosmetic damage or a broken fixture rather than injury, fire, flooding, or structural damage.
- caution: Repairs a motivated homeowner may attempt, but where mistakes can cause real cost, leaks, mild injury, or electrical issues, usually involving same-location fixture or component replacements.
- refuse: Repairs that require licensed professional or permit work, or where an amateur mistake could cause fire, flooding, structural failure, serious injury, or death.

Important boundary rules:
- Replacing an existing electrical outlet, switch, fan, fixture, or thermostat at the same location is caution.
- Adding a new outlet, new circuit, new switch location, or new wiring is refuse.
- Any electrical panel work is refuse.
- Any gas line, gas smell, gas appliance installation, or gas shutoff work is refuse.
- Removing or modifying a wall is refuse unless the user already confirms a structural engineer found it non-load-bearing.
- Replacing a water heater is refuse, but replacing minor water heater components like an anode rod or heating element may be caution.
- Installing new plumbing lines is refuse, but replacing fixtures like faucets, toilets, or showerheads is caution.
- Classify based on what the repair actually requires, not how small or easy the user says it is.
- If the question is ambiguous, choose the more cautious tier.

Return only this format:
Tier: <safe|caution|refuse>
Reason: <one sentence>
"""

    user_message = f"""
Classify this home repair question:

Question: {question}
"""

    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
        )

        raw_text = response.choices[0].message.content.strip()

        tier = None
        reason = ""

        for line in raw_text.splitlines():
            if line.lower().startswith("tier:"):
                tier = line.split(":", 1)[1].strip().lower().replace('"', "").replace("'", "")
            elif line.lower().startswith("reason:"):
                reason = line.split(":", 1)[1].strip()

        if tier not in VALID_TIERS:
            return {
                "tier": "caution",
                "reason": "The classifier response could not be parsed, so the question was handled cautiously.",
            }

        if not reason:
            reason = "The question was classified based on the home repair safety tier rules."

        return {
            "tier": tier,
            "reason": reason,
        }

    except Exception:
        return {
            "tier": "caution",
            "reason": "The classifier failed, so the question was handled cautiously.",
        }
 