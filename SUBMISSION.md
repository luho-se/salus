# Salus — Hackathon Submission

## Problem Statement

Medical self-assessment is hard. People experiencing symptoms often turn to generic search engines and end up either dismissing serious conditions or over-interpreting benign ones. The core issue is that existing tools treat everyone the same, they cannot ask targeted follow-up questions, adapt to the specific situation, or explain *why* a particular condition is being suggested.

## Solution

Salus is an AI-assisted diagnostic analysis platform that guides users through a structured, personalised symptom assessment and produces an explainable result.

When a user describes their symptoms in plain language, the system:

1. Extracts structured information automatically from the description (location, duration, severity, etc.) using an LLM, pre-filling answers on the user's behalf.
2. Generates targeted follow-up questions specific to the described symptoms.
3. Lets the user optionally request additional rounds of deeper follow-up questions for more nuance.
4. Runs the collected answers through an LLM to produce a ranked list of possible conditions, each with a probability level, a recommended care pathway (self-care, see a professional, or emergency care), a motivation, and actionable recommendations.
5. Uses **llmSHAP** (Shapley attribution for LLMs) to compute how much each individual answer influenced the diagnosis, presenting this as a visual breakdown so the user understands *what drove the result*.

The combination of structured question generation and Shapley attribution addresses two gaps at once: personalisation and explainability.

## Real-World Impact

- **Triage support** — helps users determine whether their situation warrants a urgent care, or emergency services, potentially reducing unnecessary emergency room visits and missed serious conditions.
- **Explainability** — unlike black-box symptom checkers, Salus shows which answers mattered most, building user trust and enabling more informed conversations with healthcare professionals.
- **Accessibility** — requires no medical knowledge, a plain-language description is enough to start.
- **Extensibility** — the architecture (structured Q&A + llmSHAP attribution) is domain-agnostic and could be adapted to other expert-knowledge domains beyond medicine.
