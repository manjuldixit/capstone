# Problem Framing Document

## Project Context
The ai-banking-advisory-agent is a non-transactional equipment financing support agent for business customers. It is designed to help SMEs, procurement managers, dealers, and manufacturing firms understand equipment financing products, eligibility, documentation requirements, and safe next steps.

## Problem Statement
Business customers seeking equipment financing often face fragmented product information, unclear eligibility rules, and compliance risk when discussing financing in a banking environment. The agent must provide accurate financing guidance while avoiding unauthorized transaction execution and protecting sensitive information.

## Target Users
- **SME Business Owner**: Needs guidance on equipment financing options and eligibility.
- **Procurement Manager**: Compares finance options for new equipment purchases.
- **Equipment Dealer**: Explains financing terms to customers.
- **Financing Officer**: Verifies policy-aligned recommendations.

## User Journeys
1. **Product Exploration**: User asks about equipment financing products, rates, and terms.
2. **Eligibility Assessment**: User shares business profile and credit score to discover likely approval criteria.
3. **Documentation Guidance**: User asks which documents are needed for a loan application.
4. **Safety and Escalation**: User requests an unsupported transaction or sensitive action, and the agent refuses safely.
5. **Follow-up Planning**: User asks a multi-turn question and the system retains context across the conversation.

## Success Criteria
- **Accuracy**: Responses align with the equipment financing knowledge base and policy constraints.
- **Safety**: The agent rejects transaction requests and protects PII.
- **Reliability**: The system responds consistently across user sessions and handles failure gracefully.
- **Explainability**: The agent provides reasoning or product guidance in an understandable way.
- **Practical usefulness**: The agent supports real banking workflows for equipment finance inquiries.

## Scope
Included:
- Equipment financing product descriptions
- Eligibility guidelines by credit profile
- Required documentation and application advice
- Retrieval from domain knowledge base
- Basic calculators and tool-guided guidance
- Memory-enabled multi-turn context
- Adaptive responses based on feedback

Excluded:
- Account management or balance inquiries
- Money transfers, approvals, or payment execution
- Credit decisioning or underwriting approvals
- Personal loan and consumer banking product recommendations

## Constraints and Assumptions
- The agent is non-transactional and must not execute financial actions.
- The system operates in a banking advisory context, not a sales or approval channel.
- Knowledge is grounded in a curated equipment financing knowledge base.
- Session context is maintained in-memory for demonstration.
- External tool and retrieval availability may vary, so graceful fallback is required.

## Framework and Deliverable Requirements
This project uses a phased engineering approach:
- Phase 2: Baseline LangGraph-guided agent
- Phase 3: Prompt comparison and LLM integration
- Phase 4: Retrieval-augmented generation
- Phase 5: Tool-enabled guidance
- Phase 6: Memory and multi-turn planning
- Phase 7: Adaptive behavior with feedback
- Phase 8: Deployment-ready API and UI
- Phase 9: Evaluation, failure analysis, and engineering review

## Metrics for Evaluation
- **Safety pass rate** on risk-sensitive queries
- **Quality score** of domain responses
- **Retrieval accuracy** for knowledge base queries
- **Tool success rate** for calculator and advisory actions
- **Adaptation evidence** from feedback loops
- **Documentation coverage** of design decisions and justification

## Deliverables for Submission
- Working AI agent (backend + frontend)
- Problem framing document
- Demo script with forced interactions
- Evaluation report with root-cause analysis and fix
- Engineering & product justification
- Prompt comparison evidence using 2-3 variants on the same test set
