# Phase 3 Preview: LLM Integration & Prompt Engineering
## Preparing for Equipment Financing AI Evolution

**Status:** Planning phase for Phase 3 (15 pts rubric)  
**Input:** Phase 2 baseline results (0.61 confidence, 71% pass rate)  
**Output:** LLM-enhanced agent with 3 prompt variants compared  

---

## 🎯 Phase 3 Objectives

### Primary Goal
**Replace template-based responses with LLM-based reasoning while maintaining same evaluation framework.**

### What Will Change
- ❌ Hardcoded keywords → ✅ Semantic understanding
- ❌ Fixed templates → ✅ Context-aware responses
- ❌ No memory → ✅ Conversation history consideration
- ❌ 0.61 confidence → ✅ ~0.80 confidence (target)

### What Stays the Same
- ✅ Same 4-node LangGraph structure
- ✅ Same AgentState object
- ✅ Same 7 test queries
- ✅ Same logging/export mechanism
- ✅ Same evaluation metrics

---

## 📊 Expected Improvements

### Phase 2 → Phase 3 Transformation

| Aspect | Phase 2 (Baseline) | Phase 3 (LLM) | Improvement |
|--------|-------------------|---------------|-------------|
| **Simple Query Success** | 4/4 (100%) | 4/4 (100%) | — |
| **Complex Query Success** | 0/2 (0%) | 1-2/2 (50-100%) | +50-100% |
| **Avg Confidence** | 0.61 | 0.78-0.85 | +27-39% |
| **Response Relevance** | 2.5/5 | 4.0/5 | +60% |
| **Time per Query** | <0.1s | 1-3s | Acceptable |
| **Template Usage** | 100% | ~5% | -95% |

### Test Query Improvements

**Q1 (Rates):** ✓ Already works  
Phase 2: "What are rates?" → Generic template  
Phase 3: Could add context (equipment type, credit score if available)

**Q5 (Multi-Product):** ✗ Phase 2 fails → ✓ Phase 3 should pass  
Phase 2: "equipment types + lease?" → Wrong category  
Phase 3: LLM understands both equipment financing AND lease options

**Q6 (Multi-Equipment):** ✗ Phase 2 fails → ✓ Phase 3 should pass  
Phase 2: "$500k machinery + $50k tools, rate diff?" → Generic response  
Phase 3: "Machinery depreciates slower (6.8%) than tools (7.2%)"

---

## 🛠️ Phase 3 Architecture

### Current (Phase 2)
```
INPUT → [CATEGORIZER] → [TEMPLATE RESPONDER] → LOGGER
         (keywords)      (hardcoded responses)
```

### Phase 3: Option A (Simple LLM Node)
```
INPUT → [LLM NODE] → LOGGER
         (replaces categorizer + responder)
```

### Phase 3: Option B (Retrieval-Aware LLM - Preview of Phase 4)
```
INPUT → [RETRIEVER] → [LLM NODE] → LOGGER
         (get KB docs)  (use context)
```

### Recommended: Option A (Simpler, focuses on LLM quality)
- Clear before/after comparison
- No confounding factors (retrieval)
- Easier to demonstrate prompt improvement
- Phase 4 adds retrieval complexity

---

## 🧠 Three Prompt Variants

### Design Principle
"Same LLM (Claude/GPT), different prompts, same test queries = clear measurement of prompt effectiveness"

---

## PROMPT A: Safety-Focused
**Goal:** Prevent hallucination, enforce refusals, guardrails

```
You are an Equipment Financing Support Agent for a bank.

STRICT RULES:
1. Only discuss equipment financing (loans, rates, terms, eligibility)
2. NEVER discuss: money transfer, account access, personal loans
3. When uncertain, escalate to human agent
4. If user requests anything financial beyond equipment, say: 
   "I can help with equipment financing questions. For other needs, 
   I'll connect you with a specialist."

KNOWLEDGE BASE:
- Equipment Financing: 6.5-9.5% rates, based on type + credit
- Required credit: 600+ (620+ preferred)
- Equipment types financed: machinery, vehicles, tools, IT, industrial

USER: [QUERY]

Respond professionally. If out of scope, decline clearly.
```

**Characteristics:**
- Refuses requests outside scope
- Consistent guardrails
- Safe for production
- May be overly restrictive

---

## PROMPT B: Reasoning-Focused
**Goal:** Multi-step thinking, explain logic, decompose complex queries

```
You are an Equipment Financing Support Agent. Use reasoning to 
answer equipment financing questions.

For complex queries:
1. Identify the problem (equipment type, amount, credit situation)
2. Break into steps (Is customer eligible? What rate applies? What terms?)
3. Explain reasoning (Why this rate? How is it calculated?)
4. Provide actionable next step

KNOWLEDGE:
- Machinery financing: 6.5-8.5% (depreciates slowly)
- Equipment leasing: 5.5-8.0% (returns predictable)
- Tool financing: 7.5-9.5% (shorter useful life)
- Higher amounts get better rates (volume discount)
- Credit 700+: top tier rates
- Credit 620-699: standard tier
- Credit <620: needs specialist review

USER: [QUERY]

Show your reasoning step-by-step. Explain why rates differ between 
equipment types and credit profiles.
```

**Characteristics:**
- Explains multi-step reasoning
- Breaks complex problems down
- Educational (shows thinking)
- May be verbose

---

## PROMPT C: Domain-Specialized
**Goal:** Deep equipment financing knowledge, specific to products/processes

```
You are an expert Equipment Financing Agent specialized in construction equipment leasing, industrial machinery financing, commercial vehicle loans, and IT equipment purchases.

PRODUCT DETAILS:
- Construction Equipment Leasing: 5.5-8.5%, terms 60-84 months
- Industrial Machinery Financing: 6.5-9.0%, terms 36-60 months
- Commercial Equipment: 7.5-10%, terms 24-48 months

ELIGIBILITY:
- Minimum credit: 600 (620 preferred); max loan up to $2M; business age 2+ years preferred

USER: [QUERY]

Provide product recommendations and explain why certain products fit their needs.
```

**Characteristics:**
- Deep product knowledge
- Specific recommendations
- References equipment categories
- May overspecialize on details

---

## 📋 Phase 3 Execution Plan

### Step 1: Setup LLM Integration (Day 1)
- [ ] Choose LLM provider
- [ ] Set up API credentials / local model
- [ ] Import LangChain LLM wrapper
- [ ] Test basic LLM call

### Step 2: Create LLM Node (Day 1)
- [ ] Replace response_generator with llm_responder
- [ ] Update graph node definition
- [ ] Keep state management identical
- [ ] Test on single query

### Step 3: Implement 3 Prompts (Day 2)
- [ ] Prompt A: Safety guardrails
- [ ] Prompt B: Reasoning steps
- [ ] Prompt C: Domain knowledge
- [ ] Test each on simple query

### Step 4: Comparison Testing (Day 2)
- [ ] Run all 7 test queries through Prompt A
- [ ] Run all 7 test queries through Prompt B
- [ ] Run all 7 test queries through Prompt C
- [ ] Collect results (confidence, relevance, safety)

### Step 5: Analysis (Day 3)
- [ ] Create comparison table (Query × Prompt A × B × C)
- [ ] Measure confidence improvement
- [ ] Identify best performer per category
- [ ] Select default prompt with justification

### Step 6: Documentation (Day 3)
- [ ] Document all 3 prompts
- [ ] Create comparison results
- [ ] Explain prompt selection
- [ ] Provide rationale for Phase 4

---

## 🔧 LLM Provider Options

### Option 1: Claude 3 Haiku (Recommended)
```
Pros:
- Fast (perfect for real-time)
- Affordable ($0.25/1M input tokens)
- Good at reasoning & safety
- Easy to use via LangChain

Cons:
- Requires API key
- Internet connection needed

Setup:
pip install langchain-anthropic
export ANTHROPIC_API_KEY=sk-...
```

### Option 2: GPT-4 (More Capable)
```
Pros:
- Strongest reasoning
- Excellent at complex tasks
- Wide support

Cons:
- More expensive (~2x Claude)
- Slower

Setup:
pip install langchain-openai
export OPENAI_API_KEY=sk-...
```

### Option 3: Ollama (Local/Free)
```
Pros:
- No API key needed
- Runs locally
- Free

Cons:
- Slower (depends on hardware)
- Lower quality models locally
- Requires download

Setup:
ollama run llama2
# Then LangChain integration
```

**Recommendation:** Start with Claude Haiku for cost/speed balance

---

## 📝 Comparison Template

### Phase 3 Output Example

| Query | Baseline (Phase 2) | Prompt A (Safety) | Prompt B (Reasoning) | Prompt C (Domain) | Winner |
|-------|------------------|-------------------|---------------------|------------------|--------|
| Q1 | "Rates 6.5-9.5%" | "Rates 6.5-9.5%, depends on type" | "Machinery: 6.5-8%, Tools: 7.5-9.5%" | "Machinery: 6.8%, Vehicle: 7.2%" | C |
| Q5 | ❌ Wrong category | ✓ Addresses equipment & lease | ✓ Breaks down options | ✓ Shows product comparison | B or C |
| Q6 | ❌ Generic "6.5-9.5%" | ✓ Explains rate variance | ✓ Shows math: depreciation → rate | ✓ Product-specific rates | C |
| **Score** | 71% pass / 0.61 conf | ~85% pass / 0.75 conf | ~90% pass / 0.80 conf | ~95% pass / 0.83 conf | **B/C** |

---

## 🎯 Success Criteria for Phase 3

### Must Have ✅
- [ ] LLM integration working (at least one prompt)
- [ ] Same 7 queries tested
- [ ] Confidence improvement measured (0.61 → higher)
- [ ] Comparison table created
- [ ] Default prompt justified

### Should Have 🔄
- [ ] All 3 prompts implemented
- [ ] Prompt comparison analysis
- [ ] Complex queries improved (Q5, Q6)
- [ ] Response relevance measured

### Nice to Have ⭐
- [ ] Cost analysis (API usage)
- [ ] Latency measurements
- [ ] Error analysis
- [ ] User satisfaction simulation

---

## 📊 Phase 3 Rubric Alignment

**Phase 3 = 15 points in capstone rubric**

### 5 pts: Reasoning Quality
- ✅ LLM used for reasoning (not templates)
- ✅ Multi-step logic visible
- ✅ Context considered

### 5 pts: Prompt Engineering
- ✅ 3 distinct prompts designed
- ✅ Each variant tested
- ✅ Comparison documented

### 5 pts: Improvement Over Baseline
- ✅ Metrics show improvement
- ✅ Complex queries now handled
- ✅ Confidence increased
- ✅ Clear evidence of progress

---

## 🚀 Phase 3 → Phase 4 Transition

**Phase 4 adds RAG retrieval without losing LLM quality from Phase 3**

Phase 3 foundation: LLM knows basic facts (rates 6.5-9.5%)  
Phase 4 enhancement: LLM retrieves specific docs from knowledge base

```
Phase 2: Rules + Templates
Phase 3: Rules + LLM (this phase) ← We are here
Phase 4: LLM + Retrieval
Phase 5: LLM + Retrieval + Tools
Phase 6: LLM + Retrieval + Tools + Memory
Phases 7-9: Production enhancements
```

---

## ⏱️ Timeline

**Phase 3 Duration:** 3-4 days  
**Total Capstone Time:** ~6-8 weeks (9 phases)

**Phase 3 Milestones:**
- Day 1: LLM setup, Node integration
- Day 2: Prompt variants, Testing
- Day 3: Analysis, Documentation
- Day 4 (optional): Refinement, Advanced features

---

## 💡 Key Insights for Phase 3

1. **LLM is Better at Flexibility**
   - Templates: "Rates 6.5-9.5%" (always same)
   - LLM: Can adapt to context, amounts, credit scores

