"""
Inference engine of the expert system.

It works on "facts". A fact is a short name like "http_504" and every fact
is either True (yes), False (no) or still unknown. All known facts are kept
in a dictionary called `answers`  ->  {"http_504": True, "db_slow": False}

A rule looks like:  IF http_504 AND db_queries_slow  THEN DB_SLOW_QUERY
A rule "fires" when ALL of its conditions are True.
"""
import re

from knowledge_base import RULES, QUESTIONS, KEYWORDS, DIAGNOSES


# ---------------------------------------------------------------- NLP part
def extract_facts(text):
    """Find known keywords in the user's sentence and turn them into facts.

    Example: "login gives 401 unauthorized"  ->  ["area_login", "http_401"]
    """
    text = text.lower()
    found = set()
    for phrase, fact in KEYWORDS.items():
        # \b = word boundary, so "401" does not match inside "14010"
        if re.search(r"\b" + re.escape(phrase) + r"\b", text):
            found.add(fact)
    return sorted(found)


# ------------------------------------------------------- inference part
def rule_status(rule, answers):
    """Return "fired", "failed" or "open" for one rule."""
    values = [answers.get(fact) for fact in rule["if"]]
    if all(v is True for v in values):
        return "fired"       # every condition is true
    if any(v is False for v in values):
        return "failed"      # one condition is false -> rule can never fire
    return "open"            # some conditions are still unknown


def find_diagnosis(answers):
    """Forward chaining with conflict resolution by SPECIFICITY.

    If several rules fire, the one with the most conditions wins (it is the
    most specific). If a more specific rule could still fire (it contains all
    conditions of the winner and is still open), we wait and ask more first.
    """
    fired = [r for r in RULES if rule_status(r, answers) == "fired"]
    if not fired:
        return None
    best = max(fired, key=lambda r: len(r["if"]))
    for rule in RULES:
        if rule_status(rule, answers) == "open" and set(best["if"]) < set(rule["if"]):
            return None  # e.g. "502 + restarts" may still become "502 + restarts + memory"
    return best


def matched(rule, answers):
    """How many conditions of this rule are already true."""
    return sum(1 for fact in rule["if"] if answers.get(fact) is True)


def next_question(answers):
    """Choose the next fact to ask the user about.

    1. Keep only rules that can still fire ("open").
    2. Keep the ones closest to firing (most true conditions).
    3. Ask the unknown fact shared by most of those rules, because its answer
       confirms or removes the most rules at once. Irrelevant questions are
       never asked.
    """
    open_rules = [r for r in RULES if rule_status(r, answers) == "open"]
    if not open_rules:
        return None

    top = max(matched(r, answers) for r in open_rules)
    closest = [r for r in open_rules if matched(r, answers) == top]

    counts = {}
    for rule in closest:
        for fact in rule["if"]:
            if fact not in answers:
                counts[fact] = counts.get(fact, 0) + 1
    return max(counts, key=counts.get)  # ties -> the fact seen first


def explain(rule, answers):
    """Produce a human readable reasoning trace for the fired rule."""
    lines = []
    for fact in rule["if"]:
        lines.append(f"✔ {QUESTIONS[fact]}  →  YES")
    diagnosis = DIAGNOSES[rule["then"]]
    lines.append(f"All conditions of rule {rule['id']} are true, so it fires.")
    lines.append(f"So the most likely cause is: {diagnosis['name']} "
                 f"({diagnosis['layer']} layer), confidence {int(rule['cf'] * 100)}%.")
    return lines
