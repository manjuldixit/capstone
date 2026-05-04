import traceback
from pathlib import Path
from adaptive_agent import EquipmentFinancingAdaptiveAgent

try:
    base_dir = Path(__file__).resolve().parent
    agent = EquipmentFinancingAdaptiveAgent(
        kb_path=str(base_dir / 'data' / 'knowledge_base.json'),
        retriever_db_path=str(base_dir / 'data' / 'chroma_db'),
        max_tool_calls=4,
        short_term_capacity=10
    )
    print('agent created')
    result = agent.process_query('What are the equipment financing rates?')
    print(result)
except Exception:
    traceback.print_exc()
