# Engineering & Product Justification

## Product Goals
The ai-banking-advisory-agent is designed to support equipment financing conversations while maintaining safety, compliance, and practical usefulness in business workflows.

### Core product goals
- Help customers compare equipment financing products
- Explain eligibility and documentation requirements
- Avoid unauthorized transactions and protect sensitive data
- Support decision-making with grounded references
- Deliver a predictable and safe user experience

## Engineering Choices
### Why this architecture?
The project follows a phased, modular design to balance reliability with feature evolution.
- **Baseline agent first**: Establish a working conversational foundation before adding complexity.
- **Prompt experiments**: Compare prompt variants to validate reasoning, domain expertise, and safety behavior.
- **Retrieval layer**: Ground answers in real knowledge base content to reduce hallucinations.
- **Tool layer**: Add concrete calculations and structured assistance for finance scenarios.
- **Memory & planning**: Maintain context across multi-turn dialogues for practical workflows.
- **Adaptation**: Use feedback to improve response specificity and customer relevance.

### Framework decisions
- **Framework-free baseline**: The initial agent is simple, readable, and easy to debug.
- **Selective framework usage**: The project only uses supporting libraries where they provide clear benefit (FastAPI for API hosting, Streamlit for frontend, LangChain-style retrieval patterns).
- **Minimal dependency approach**: Avoid unnecessary frameworks that add complexity without value.

## Safety-first design
### Safety as a feature
- **Guardrails** prevent unauthorized money movement and out-of-scope advice.
- **PII protection** is treated as non-negotiable.
- **Escalation logic** ensures ambiguous or risky requests are handled safely.
- **Graceful degradation** ensures the agent still responds usefully if retrieval or tools fail.

### Practical risk controls
- If retrieval fails, the agent falls back to a safe baseline response.
- If tools fail, the agent explains the error and provides next steps.
- For sensitive user requests, the system refuses politely and suggests secure channels.

## Why this product is useful
### Real workflow alignment
The agent supports workflows common in equipment financing:
- product research and comparison
- eligibility screening before loan application
- documentation preparation
- clarifying financing terms
- safe escalation of non-routine requests

### Business value
- reduces support load on human agents
- speeds up customer decision-making
- improves consistency of advisory responses
- strengthens compliance by preventing unsafe transactions

## Trade-offs and justification
### Trade-off: Simplicity vs. breadth
- The project favors a narrower, safer domain (equipment financing) over broad banking advice.
- This improves reliability and reduces hallucination risk.

### Trade-off: In-memory sessions vs. persistence
- Current implementation uses in-memory state for demo speed and simplicity.
- A production-ready system should add persistent storage for session continuity, but this is deferred to later phases.

### Trade-off: Framework-free vs. agent frameworks
- The baseline is intentionally framework-free to keep control over logic.
- Retrieval and adaptation are introduced incrementally so framework usage is justified by actual need, not academic novelty.

## Deliverable validation
The submission package is designed to provide clear evidence for:
- a working AI agent
- a documented problem framing
- a forced demo script
- evaluation and root cause analysis
- engineering/product justification
- prompt comparison evidence
