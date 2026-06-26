# Spec: `classify_safety_tier()`

**File:** `safety.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, or should be refused with a referral to a licensed professional.

---

## Input / Output Contract

**Input:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key | Type | Description |
|-----|------|-------------|
| `"tier"` | `str` | One of: `"safe"`, `"caution"`, `"refuse"` |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Tier definitions

*Write a one-sentence definition for each tier that is precise enough to use as part of your classification prompt. Vague definitions produce inconsistent classifications.*

**safe:**
```
Routine DIY repairs that most homeowners can complete with basic tools, where mistakes usually cause only cosmetic damage or a broken fixture rather than injury, fire, flooding, or structural damage.
```

**caution:**
```
Repairs a motivated homeowner may attempt, but where mistakes can cause real cost, leaks, mild injury, or electrical issues, usually involving same-location fixture or component replacements.
```

**refuse:**
```
Repairs that require licensed professional or permit work, or where an amateur mistake could cause fire, flooding, structural failure, serious injury, or death.
```

---

### Classification approach

*How will the LLM classify the question? Will you give it just the tier definitions, or also examples (few-shot)? Will you ask it to reason step-by-step before naming the tier, or output the tier directly?*

*Consider: what happens when a question is genuinely ambiguous — e.g., "can I replace my own outlets?" Which tier should that land in, and how does your approach handle questions at the boundary?*

```
I will give the LLM clear tier definitions plus few-shot examples, especially edge cases around replacing existing components versus adding new systems. I will ask it to make a concise classification and provide one short reason, but not a long step-by-step explanation, because the output needs to be easy to parse. If a question is ambiguous, the classifier should choose the more cautious tier rather than assuming the repair is safe.
```

---

### Output format

*How will the LLM communicate the tier and reason back to you? Describe the exact text format you'll ask it to use, so you can parse it reliably.*

*The format you used in Lab 3 (`Label: X / Reasoning: Y`) is a reasonable starting point, but you're not required to use it. Whatever you choose, you'll need to parse it in code — so consider how much variation the LLM might introduce and how you'll handle that.*

```
The LLM should return exactly two lines:

Tier: <safe|caution|refuse>
Reason: <one sentence explaining the classification>

This format is easy to parse because the tier is always after "Tier:" and the reason is always after "Reason:".
```

---

### Prompt structure

*Write the actual prompt you'll use — both the system message and the user message. Don't describe it — write it. Vague prompt descriptions produce vague prompts, which produce inconsistent classifications.*

**System message:**
```
You are a safety classifier for a home repair assistant. Your job is to classify the user's repair question into exactly one tier: safe, caution, or refuse.

Tier definitions:

safe: Routine DIY repairs that most homeowners can complete with basic tools, where mistakes usually cause only cosmetic damage or a broken fixture rather than injury, fire, flooding, or structural damage.
caution: Repairs a motivated homeowner may attempt, but where mistakes can cause real cost, leaks, mild injury, or electrical issues, usually involving same-location fixture or component replacements.
refuse: Repairs that require licensed professional or permit work, or where an amateur mistake could cause fire, flooding, structural failure, serious injury, or death.

Important boundary rules:

Replacing an existing electrical outlet, switch, fan, fixture, or thermostat at the same location is caution.
Adding a new outlet, new circuit, new switch location, or new wiring is refuse.
Any electrical panel work is refuse.
Any gas line, gas smell, gas appliance installation, or gas shutoff work is refuse.
Removing or modifying a wall is refuse unless the user already confirms a structural engineer found it non-load-bearing.
Replacing a water heater is refuse, but replacing minor water heater components like an anode rod or heating element may be caution.
Installing new plumbing lines is refuse, but replacing fixtures like faucets, toilets, or showerheads is caution.
Classify based on what the repair actually requires, not how small or easy the user says it is.
If the question is ambiguous, choose the more cautious tier.

Return only this format:
Tier: <safe|caution|refuse>
Reason: <one sentence>
```

**User message:**
```
Classify this home repair question:
```

---

### Caution/refuse boundary

*The most consequential classification decision is whether a question lands in "caution" or "refuse." Write down your rule for this boundary — one sentence. Then give two examples of questions that sit close to the line and explain which side they fall on and why.*

```
If the repair requires new wiring, electrical panel work, gas work, structural changes, new plumbing lines, a permit/licensed professional, or could cause fire, flooding, structural failure, serious injury, or death if done wrong, classify it as refuse instead of caution.

Example 1: "Can I replace an electrical outlet that stopped working?" should be caution because it is a same-location component swap on an existing circuit.

Example 2: "Can I add a new electrical outlet to my garage?" should be refuse because adding a new outlet requires new wiring and may involve panel work, which creates a hidden fire hazard if done incorrectly.
```

---

### Fallback behavior

*What does your function return if the LLM response can't be parsed — e.g., if it produces free-form prose instead of your expected format? What happens when tier validation against `VALID_TIERS` fails?*

*Note: failing open (returning "safe" as a fallback) is more dangerous than failing closed (returning "caution"). Which makes more sense here, and why?*

```
If the LLM response cannot be parsed or the tier is not one of the allowed values, the function should return {"tier": "caution", "reason": "The classifier response could not be parsed, so the question was handled cautiously."}

This is safer than returning "safe" because failing open could cause the assistant to provide confident DIY instructions for a risky repair.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 2.*

**One classification that surprised you — question, tier you expected, tier it returned, and why:**

```
I expected replacing an electrical outlet to maybe be classified as refuse, but it was classified as caution because it is a same-location component replacement on an existing circuit rather than new electrical work.

```

**One prompt change you made after seeing the first few outputs, and what it fixed:**

```
I added explicit rules distinguishing replacing an existing outlet from adding a new outlet. This fixed the edge case where both questions might otherwise be treated the same.
```
