# Phase 2 Quick Start Guide
## ai-banking-advisory-agent Backend — LangGraph Baseline Equipment Financing Agent

**Status:** ✅ Complete & Ready to Run  
**Location:** `ai-banking-advisory-agent/backend/`  
**Framework:** LangGraph  
**Language:** Python 3.10+

---

## 📋 Prerequisites

```bash
# Install dependencies
cd ai-banking-advisory-agent/backend
pip install -r requirements.txt
```

**Required Packages:**
- langgraph (graph orchestration)
- langchain (LLM integration foundation)
- pandas (results analysis)
- python-dotenv (configuration)

---

## 🚀 Run the Agent

### Option 1: Demo Script (Recommended)
```bash
cd ai-banking-advisory-agent/backend
python run_phase2_demo.py
```

**Output:**
- 10-section demonstration
- 7 test queries executed
- Detailed results table
- Limitation documentation
- Metrics analysis
- Logs exported to `baseline_logs.json`

### Option 2: Direct Agent Execution
```bash
python -c "from langgraph_agent import EquipmentFinancingBaseline; agent = EquipmentFinancingBaseline(); agent.process_query('What are the rates?'); agent.export_logs()"
```

---

## 📊 Expected Output

### Demo Script Sections
1. **Initialization** - Agent setup confirmation
2. **Test Queries** - 7 queries defined
3. **Execution** - Query processing with results
4. **Results Table** - Pass/fail summary
5. **Metrics** - Overall performance stats
6. **Detailed Responses** - Full responses shown
7. **Limitations** - 3 documented limitations
8. **Sufficiency Analysis** - Why baseline needs LLM
9. **Improvements** - Phase 3 opportunities
10. **Export & Summary** - Logs and final report

### Key Metrics
```
Pass Rate: 71% (5/7 queries)
Simple Queries: 4/4 (100%)
Complex Queries: 0/2 (0%)
Escalation: 1/1 (100%)
Average Confidence: 0.61
```

---

## 📁 File Structure

```
ai-banking-advisory-agent/
├── backend/
│   ├── langgraph_agent.py          ← Core agent (450+ lines)
│   ├── run_phase2_demo.py          ← Demo script (run this)
│   ├── requirements.txt            ← Dependencies
│   └── baseline_logs.json          ← Generated on run
│
├── data/
│   ├── knowledge_base.json         ← Equipment financing facts
│   └── evaluation_test_set.json    ← Test queries
│
├── frontend/                       ← For future UI
│   └── [placeholder]
│
├── docs/
│   ├── PHASE_2_QUICK_START.md      ← This file
│   ├── PHASE_2_SUMMARY.md          ← Architecture details
│   └── PHASE_2_COMPLETION_SUMMARY.md
│
└── README.md                       ← ai-banking-advisory-agent overview
```

---

## ⚙️ Configuration

### Knowledge Base Path
By default, agent loads KB from `../data/knowledge_base.json`

To use custom KB:
```python
from langgraph_agent import EquipmentFinancingBaseline
agent = EquipmentFinancingBaseline(kb_path="path/to/custom_kb.json")
```

### Logging Level
```python
import logging
logging.basicConfig(level=logging.DEBUG)  # More verbose
```

---

## 🏗️ Architecture Overview

### 4-Node LangGraph Workflow

```
User Query
    ↓
[INPUT_PROCESSOR]
├─ Validate input
├─ Check PII
├─ Initialize state
    ↓
[CATEGORIZER] ← LIMITATION 1
├─ Keyword matching
├─ Fixed categories
├─ Assign confidence
    ↓
[RESPONSE_GENERATOR] ← LIMITATION 2
├─ Template lookup
├─ Return template
├─ No personalization
    ↓
[LOGGER]
├─ Store interaction
├─ Export to JSON
├─ Track metrics
    ↓
Response + Metadata

(LIMITATION 3: No multi-turn memory)
```

---

## 📊 Understanding Test Results

### Query Categories

| Category | Example | Result |
|----------|---------|--------|
| EQUIPMENT_RATES | "What are rates?" | ✓ PASS |
| LOAN_TERMS | "What are terms?" | ✓ PASS |
| ELIGIBILITY | "700 credit, qualify?" | ✓ PASS |
| PROCESS | "How long?" | ✓ PASS |
| EDUCATION (Multi) | "Equipment types + lease?" | ✗ FAIL |
| COMPLEX (Multi-item) | "Machinery $500k + tools $50k?" | ✗ FAIL |
| ESCALATION | "Approve me now" | ✓ PASS |

### Why 71% Pass Rate?

✓ **Simple queries work** (4/4):
- Exact keyword matches
- Fit predefined categories
- Template responses work

✗ **Complex queries fail** (0/2):
- Multiple topics in one query
- Need semantic understanding
- Templates insufficient

✓ **Escalation handled** (1/1):
- Appropriate refusal/escalation
- Safety mechanisms work

---

## ⚠️ Three Documented Limitations

### LIMITATION 1: Hardcoded Keyword Matching
- Fixed keyword lists can't understand semantic variations
- Example: "equipment types + lease" → only "equipment" matches
- Result: Wrong category → wrong response

### LIMITATION 2: Template Responses
- Each category has one fixed response
- No context awareness or personalization
- Example: "$500k machinery + $50k tools" → generic rate response

### LIMITATION 3: No Memory
- Each query independent
- No conversation history
- Example: User mentions "700 credit" in Q1 → Q2 ignores it

---

## 🔍 Inspecting Logs

### View Generated Logs
```python
import json

with open("baseline_logs.json", "r") as f:
    logs = json.load(f)
    
print(f"Total interactions: {logs['total_interactions']}")
for interaction in logs['interactions']:
    print(f"Query: {interaction['query']}")
    print(f"Category: {interaction['category']}")
    print(f"Confidence: {interaction['confidence']}")
```

### Log Structure
```json
{
  "timestamp": "2026-05-02T...",
  "agent_type": "langgraph_baseline",
  "session_id": "baseline_20260502_...",
  "total_interactions": 7,
  "interactions": [
    {
      "timestamp": "...",
      "session_id": "...",
      "turn": 1,
      "query": "What are current rates?",
      "response": "Our equipment financing rates...",
      "category": "equipment_rates",
      "confidence": 0.60,
      "sources": [],
      "metadata": {...}
    },
    ...
  ]
}
```

---

## 🐛 Troubleshooting

### Import Error: "No module named 'langgraph'"
```bash
pip install langgraph langchain-core
```

### FileNotFoundError: "knowledge_base.json"
- Verify `ai-banking-advisory-agent/data/knowledge_base.json` exists
- Agent has default KB if file missing

### Logs not exporting
```python
agent.export_logs("baseline_logs.json")
# Check write permissions on folder
```

### High memory usage
- Normal for LangGraph (stores all state)
- 7 queries ≈ 1-2 MB logs

---

## ✅ Verification Checklist

- [ ] Python 3.10+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Can run: `python run_phase2_demo.py`
- [ ] Output shows 7 queries executed
- [ ] `baseline_logs.json` created in backend folder
- [ ] Pass rate shown as 71%
- [ ] Limitations documented in output

---

## 📈 Next Steps (Phase 3)

After Phase 2 baseline:
1. Review limitations in output
2. Understand why 0% on complex queries
3. Proceed to Phase 3: LLM Integration
4. Replace templates with LLM reasoning
5. Test 3 prompt variants
6. Measure improvement (0.61 → 0.80+ confidence)

---

## 📞 Support

// - **Phase 3 Planning:** See `PHASE_3_PREVIEW_AND_PLANNING.md`
---

**Status:** Phase 2 ✅ Ready to Execute  
**Next:** Phase 3 - LLM Integration  
**Timeline:** 3-4 days for Phase 3

Run the demo script now and see your baseline in action! 🚀

