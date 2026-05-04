# Equipment Financing AI Agent — Capstone Project (Moved)
## Agentic AI Platform Implementation

**Status:** Phase 2 ✅ Complete | Phase 3 🚀 Ready  
**Framework:** LangGraph  
**Domain:** Equipment Financing Support (Non-Transactional)  
**Rubric Points:** 100 total across 9 phases

---

## 🎯 Project Overview

### What You're Building
An AI agent that helps customers inquire about equipment financing options, eligibility, and loan terms in a banking context. The agent evolves through 9 phases from rule-based baseline to production-grade agentic system.

### Key Features
- ✅ **Phase 2 Complete:** Rule-based baseline with 4-node LangGraph
- ✅ **Phase 3 Ready:** LLM integration with prompt engineering
- 📋 **Phases 4-9:** Retrieval, tools, memory, adaptation, deployment, evaluation

### Submission Deliverables
- **PROBLEM_FRAMING.md** — problem definition, personas, scope, and success criteria
- **DEMO_SCRIPT.md** — forced interaction script for retrieval, tool usage, memory, adaptation, and safety
- **EVALUATION_REPORT.md** — evaluation approach, prompt comparison, root cause, and fixes
- **ENGINEERING_PRODUCT_JUSTIFICATION.md** — architecture, safety-first design, and practical justification

### Why This Matters
- Equipment financing is high-value (products worth thousands)
- Customers want quick education, rates, eligibility checks
- Non-transactional focus (no money movement by agent)
- Clear rubric to demonstrate agent evolution

---

## 📂 Project Structure

```
Capstone/
├── README.md                          ← (moved here)
├── ROADMAP_AND_GUIDE.md              ← Phase-by-phase guide
├── MASTER_CAPSTONE_PROGRESS.ipynb    ← Progress tracker
├── PHASE_3_PREVIEW_AND_PLANNING.md   ← What's coming next
│
├── phase_1_problem_framing/
│   ├── PROBLEM_FRAMING.md            ← Domain analysis, personas, workflows
│   └── [Supporting documents]
│
├── phase_2_baseline/
│   ├── langgraph_agent.py            ← Main LangGraph agent (450+ lines)
│   ├── Phase_2_LangGraph_Baseline.ipynb  ← Demo notebook
│   ├── PHASE_2_LANGGRAPH_SUMMARY.md      ← Architecture & results
│   ├── PHASE_2_QUICK_START.md            ← How to run
│   ├── PHASE_2_COMPLETION_SUMMARY.md     ← What was delivered
│   └── baseline_logs.json            ← Auto-generated logs
│
├── phase_3_llm_integration/          ← [In Progress]
│   ├── llm_agent.py
│   ├── prompt_variants.py
│   ├── Phase_3_LLM_Comparison.ipynb
│   └── [Documentation]
│
├── data/
│   ├── knowledge_base.json           ← Equipment financing facts
│   ├── evaluation_test_set.json      ← 15 test queries
│   └── [Training data if applicable]
│
├── [phases_4_to_9]/                  ← Folders for future phases
│   ├── phase_4_retrieval/
│   ├── phase_5_tools/
│   ├── phase_6_memory/
│   ├── phase_7_adaptation/
│   ├── phase_8_deployment/
│   └── phase_9_evaluation/
│
└── docs/
    ├── ARCHITECTURE.md
    ├── DESIGN_DECISIONS.md
    └── [Additional documentation]
```

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.10+
pip install langgraph langchain-core pandas jupyter
```

### Run Phase 2 (Baseline Agent)
```bash
cd Capstone/phase_2_baseline
jupyter notebook Phase_2_LangGraph_Baseline.ipynb
```

Expected output: 7 test queries executed, logs exported, limitations documented

### Check Results
```bash
# View baseline_logs.json for interaction logs
# Review Phase_2_LANGGRAPH_SUMMARY.md for detailed analysis
```

---

*(Original `capstone/README.md` moved to `capstone/ai-banking-advisory-agent/docs/README.md`.)*

