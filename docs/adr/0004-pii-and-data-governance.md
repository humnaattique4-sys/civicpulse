# ADR 0004: PII and Data Governance

## Status
Accepted

## Context
Citizen complaints may contain personal information — names, addresses, phone numbers — either in the free-text complaint body or the optional `reporter_contact` field. The assignment requires an explicit decision about what data leaves the system and to whom, rather than leaving this unaddressed.

## Decision
The current triage provider (`RuleBasedTriage`) is fully local — it runs keyword matching inside our own backend container and sends no data to any third party. No complaint text or contact information leaves our infrastructure at any point in the triage pipeline.

If an LLM-backed provider (e.g. calling a hosted model like Groq or Gemini) is added later, we will:
1. Never send the `reporter_contact` field to the external provider — only the complaint `text` and `location` fields are relevant to triage.
2. Document, per provider, whether the vendor's free tier uses submitted input to improve their models (as some free tiers do), and treat that as a factor in provider selection rather than an afterthought.
3. Prefer providers with a no-training-on-input guarantee where cost allows, and fall back to `RuleBasedTriage` or a local model (e.g. Ollama) for any deployment where PII exposure is unacceptable.

## Consequences
- Today, there is zero external PII exposure, since triage is fully local.
- If we add a hosted LLM provider, `reporter_contact` must be explicitly excluded from the payload sent to that provider — a deliberate code-level decision, not an accident of what fields happen to be in scope.
- This decision trades classification accuracy (rule-based matching is less nuanced than an LLM) for a stronger privacy guarantee, which we consider the right default for a municipal system handling citizen data.