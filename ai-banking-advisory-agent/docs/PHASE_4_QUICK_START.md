# Phase 4: Knowledge & Retrieval — Quick Start

## 🎯 What is Phase 4?

Phase 4 adds **semantic search and retrieval-augmented generation (RAG)** to the agent:
- **Baseline (Phase 2)**: Rule-based, keyword matching, template responses
- **Phase 3**: LLM integration for more natural responses
- **Phase 4**: Semantic retrieval + source grounding (YOU ARE HERE)

### Key Improvements
✅ **Semantic Understanding**: Query embedding + document similarity matching  
✅ **Context Grounding**: Responses cite actual knowledge base content  
✅ **Improved Accuracy**: Retrieved documents prevent hallucination  
✅ **Source Transparency**: Users see what information was used  

---

## 📦 Installation

### Install Dependencies
```bash
cd capstone/ai-banking-advisory-agent/backend
pip install -r requirements.txt
```

The new Phase 4 packages:
- `chromadb>=0.3.21` — Vector database for embeddings
- `sentence-transformers>=2.2.0` — Embedding models (all-MiniLM-L6-v2)
- `numpy>=1.24.0` — Numerical operations

---

## 🚀 Quick Start (5 minutes)

### 1. Initialize Vector Store (First Run Only)

```bash
cd capstone/ai-banking-advisory-agent/backend
python -c "
from vector_store import initialize_retriever
manager = initialize_retriever(force_reinit=True)
print('Vector store initialized!')
print('Documents indexed:', manager.get_stats()['document_count'])
"
```

This will:
- Parse knowledge base into semantic chunks
- Generate embeddings using sentence-transformers
- Store in Chroma database at `data/chroma_db/`
- Export processed documents to `data/processed_documents.json`

### 2. Test Retrieval

```bash
python -c "
from vector_store import RetrieverManager
manager = RetrieverManager()
results = manager.retrieve('What are the rates for equipment financing?', top_k=3)
for r in results:
    print(f'[{r[\"rank\"]}] Similarity: {r[\"similarity_score\"]}')
    print(f'    {r[\"content\"][:150]}...\n')
"
```

### 3. Run Full Comparison (Phase 2 vs Phase 4)

```bash
python run_phase4_compare.py --force-reinit
```

**Output**:
- `outputs/phase4_comparison_{timestamp}.json` — Detailed per-query comparison
- Terminal summary with aggregate metrics

**What it measures**:
- Confidence scores (baseline vs RAG)
- Retrieved sources per query
- Source coverage percentage
- Confidence improvement

### 4. Review Results

```bash
# View JSON results
cat outputs/phase4_comparison_*.json | python -m json.tool | head -100

# Key metrics in the JSON:
# - aggregate_metrics.improvement.average_confidence_delta
# - aggregate_metrics.rag.source_coverage
# - aggregate_metrics.rag.average_sources
```

---

## 🏗️ Architecture Overview

### Components

#### 1. **Document Processor** (`document_processor.py`)
Converts knowledge base JSON into embeddable chunks:
- Extracts products, eligibility, application process, FAQs
- Flattens hierarchical structure
- Preserves metadata (source, type, category)
- ~40-60 semantic documents

**Key Class**: `DocumentProcessor`
```python
processor = DocumentProcessor("data/knowledge_base.json")
documents = processor.process()
```

#### 2. **Vector Store** (`vector_store.py`)
Manages embeddings and semantic retrieval:
- Chroma database for vector storage
- Sentence-transformers for embedding model
- Cosine similarity for retrieval
- Stats tracking (retrieval count, coverage, sources)

**Key Classes**: `VectorStore`, `RetrieverManager`
```python
manager = RetrieverManager()
results = manager.retrieve(query, top_k=3)
# Returns: list of dicts with content, metadata, similarity_score
```

#### 3. **RAG Agent** (`rag_agent.py`)
Extends Phase 2 baseline with retrieval:
- Inherits from `EquipmentFinancingBaseline`
- Retrieves context before generating response
- Augments response with source citations
- Tracks retrieval performance

**Key Class**: `EquipmentFinancingRAG`
```python
agent = EquipmentFinancingRAG()
result = agent.process_query("What rates do you offer?")
# result includes: response, confidence, sources, retrieval_stats
```

#### 4. **Comparison Runner** (`run_phase4_compare.py`)
Side-by-side evaluation:
- Loads test queries from evaluation set
- Runs through baseline agent (no retrieval)
- Runs through RAG agent (with retrieval)
- Compares confidence, sources, coverage
- Exports detailed JSON report

---

## 💡 How It Works (Simple Example)

**User Query**: "What equipment can I finance?"

### Phase 2 Baseline Flow
```
1. Input Validation ✓
2. Keyword Categorization → "equipment_types"
3. Template Lookup → Hardcoded response
4. Return → "We offer commercial equipment, construction..." (generic)
```

### Phase 4 RAG Flow
```
1. Input Validation ✓
2. Convert query to embedding (vector)
3. Semantic Search in Vector Store
   - Find similar documents (products, eligibility, equipment types)
   - Top 3 matches with similarity scores
4. Augment Response
   - Use template + retrieved documents
   - Cite specific rate ranges, equipment types, credit requirements
5. Return → Same template + "Based on knowledge base: [specific details]"
   - Confidence ↑ (0.7 → 0.8)
   - Sources ✓ (shows what was retrieved)
```

---

## 📊 Expected Results

From baseline → RAG:

| Metric | Phase 2 | Phase 4 | Change |
|--------|--------|--------|--------|
| Avg Confidence | 0.65 | 0.75 | +15% |
| Queries with Sources | 0/10 | 8/10 | +80% |
| Avg Sources per Query | 0 | 2.4 | N/A |
| Hallucination Risk | High | Low | ✓ |

---

## 🔧 Configuration

### Environment Variables

Create `.env` in `capstone/ai-banking-advisory-agent/backend/`:
```bash
# Vector Store
CHROMA_DB_PATH=data/chroma_db
COLLECTION_NAME=equipment_financing
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Retrieval
TOP_K_RESULTS=3
SIMILARITY_THRESHOLD=0.3
```

### Advanced: Custom Embedding Model

```python
from vector_store import VectorStore

# Use larger model for better quality (slower)
store = VectorStore(
    embedding_model="all-mpnet-base-v2"  # ~430M params
)

# Or faster, smaller model
store = VectorStore(
    embedding_model="all-MiniLM-L6-v2"  # ~22M params
)
```

---

## ⚠️ Known Limitations & Next Steps

### Current Limitations (Phase 4)
- ✗ Single document retrieval (no multi-hop reasoning)
- ✗ No feedback loop (user can't rate relevance)
- ✗ Fixed vector store (updates require re-embedding)
- ✗ No caching (each query hits embeddings)

### Phase 5 Preview: Tools & Actions
- [ ] Add external API tools (credit check, rate calc)
- [ ] Implement agent tools system
- [ ] Enable tool use decisions

### Phase 6 Preview: Memory & Conversation
- [ ] Multi-turn conversation memory
- [ ] User profile persistence
- [ ] Personalized responses

---

## 📝 Example: Custom Retrieval Query

```python
from rag_agent import EquipmentFinancingRAG

agent = EquipmentFinancingRAG()

# Query 1: Product inquiry
result = agent.process_query(
    "What's the difference between commercial equipment financing and construction leasing?"
)
print(result["response"])
print(f"Confidence: {result['confidence']}")
print(f"Sources: {[s['product_name'] for s in result['sources'] if 'product_name' in s]}")

# Query 2: Eligibility question
result2 = agent.process_query(
    "I have a 680 credit score. Can I apply?"
)
print(result2["response"])

# Export logs
agent.export_rag_logs("outputs")
```

---

## 📚 File Structure

```
capstone/ai-banking-advisory-agent/backend/
├── requirements.txt                    ← Add chromadb, sentence-transformers
├── langgraph_agent.py                  ← Phase 2 baseline (inherited by Phase 4)
├── document_processor.py               ← NEW: Chunk knowledge base
├── vector_store.py                     ← NEW: Chroma + retrieval
├── rag_agent.py                        ← NEW: RAG agent (extends baseline)
├── run_phase4_compare.py              ← NEW: Phase 2 vs Phase 4 comparison
│
├── data/
│   ├── knowledge_base.json
│   ├── evaluation_test_set.json
│   ├── chroma_db/                      ← NEW: Vector store (auto-created)
│   └── processed_documents.json        ← NEW: Exported chunks
│
└── outputs/
    └── phase4_comparison_*.json        ← NEW: Comparison results
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'chromadb'"
```bash
pip install chromadb sentence-transformers
```

### Issue: Vector store not initializing
```bash
# Clear and reinit
rm -rf data/chroma_db
python run_phase4_compare.py --force-reinit
```

### Issue: Memory usage too high
- Reduce `top_k` in retrieval (default 3)
- Use smaller embedding model: `all-MiniLM-L6-v2` (22M params)
- Disable Chroma telemetry in `vector_store.py`

---

## ✅ Validation Checklist

Before moving to Phase 5, verify:

- [ ] Vector store initialized with ~40+ documents
- [ ] Retrieval returns relevant results (similarity > 0.3)
- [ ] RAG agent confidence > baseline confidence
- [ ] Source coverage > 70% of queries
- [ ] No errors in comparison runner
- [ ] Outputs exported to JSON

Run this to check:
```bash
python -c "
from rag_agent import EquipmentFinancingRAG
agent = EquipmentFinancingRAG()
stats = agent.get_retrieval_stats()
print(f'✓ Retrieval success rate: {stats[\"success_rate\"]:.1%}')
print(f'✓ Avg similarity: {stats[\"average_similarity\"]:.3f}')
print(f'✓ Sources tracked: {len(stats[\"sources_used\"])} types')
"
```

---

## 🎓 Learning Path

1. **Understand RAG**: Read the comparison output JSON
2. **Modify retrieval**: Change `top_k` and observe impact
3. **Try different queries**: Test edge cases
4. **Explore embeddings**: Use the `processed_documents.json` to see chunks
5. **Extend retrieval**: Add custom retrieval scoring in `vector_store.py`

---

## 📞 Next Steps

- Phase 5: Add Tools & External APIs (credit checks, rate calculators)
- Phase 6: Multi-turn Memory & Personalization
- Phase 7: Adaptive Behavior (learn from interactions)

For detailed Phase 4 planning, see [PHASE_3_PREVIEW_AND_PLANNING.md](PHASE_3_PREVIEW_AND_PLANNING.md).

