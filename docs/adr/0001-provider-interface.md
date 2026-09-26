# ADR 0001: Triage Provider Interface

## Status
Accepted

## Context
The system needs to classify citizen complaints into a category, priority, and summary. Today this is done with keyword rules, but the assignment brief is explicit that this reader must be replaceable — tomorrow it could be an LLM, next year a fine-tuned classifier. The system must not depend on which one is active, and must not break when the "smart" one is slow, rate-limited, or wrong.

## Decision
We defined a `TriageProvider` interface (Python `Protocol`) with a single method:

```python
def triage(self, text: str, location: str) -> TriageResult: ...
```

`TriageResult` is a Pydantic model with `category`, `priority`, `summary`, and `confidence` fields, so every provider — regardless of implementation — returns a validated, schema-conformant result.

We currently ship one implementation, `RuleBasedTriage`, selected via the `TRIAGE_PROVIDER` environment variable. It uses keyword matching against the complaint text to assign a category, and checks for urgency-indicating words (e.g. "flooding", "burst", "fire") to assign priority.

## Consequences
- Adding an LLM-backed provider later (e.g. `LLMTriage` calling Groq) requires no changes to the API routes, database schema, or frontend — only a new class implementing the same interface, selected by environment variable.
- The rule-based provider is fully deterministic, has zero external dependencies, and never fails — making it a safe default and a natural fallback for when an LLM provider times out or returns malformed output.
- The trade-off is lower classification accuracy compared to an LLM, especially for ambiguous or multi-category complaints (e.g. a complaint mentioning both a "street" and a "streetlight" needs careful keyword ordering to avoid misclassification — a real bug we hit and fixed during development).