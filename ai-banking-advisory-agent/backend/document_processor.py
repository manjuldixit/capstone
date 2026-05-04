"""
Document Processor for Phase 4: Knowledge & Retrieval
Handles document chunking, metadata extraction, and preparation for embedding
"""

import json
import logging
from typing import List, Dict, Any
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a chunk of text with metadata"""
    content: str
    metadata: Dict[str, Any]
    doc_id: str


class DocumentProcessor:
    """
    Processes knowledge base JSON into embeddable documents.
    
    Strategy:
    - Flatten hierarchical JSON into semantic chunks
    - Preserve source metadata (product type, section, etc.)
    - Target chunk size ~200-400 words for optimal embedding
    """
    
    def __init__(self, kb_path: str):
        """Initialize processor with knowledge base path"""
        self.kb_path = Path(kb_path)
        self.knowledge_base = self._load_kb()
        self.documents: List[Document] = []
    
    def _load_kb(self) -> Dict[str, Any]:
        """Load knowledge base JSON"""
        try:
            with open(self.kb_path, 'r') as f:
                kb = json.load(f)
            logger.info(f"Loaded knowledge base from {self.kb_path}")
            return kb
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            raise
    
    def process(self) -> List[Document]:
        """
        Process entire knowledge base into documents.
        Returns list of Document objects ready for embedding.
        """
        self.documents = []
        
        # 1. Process Equipment Financing Products
        if "equipment_financing_products" in self.knowledge_base:
            self._process_products(self.knowledge_base["equipment_financing_products"])
        
        # 2. Process Eligibility Criteria
        if "eligibility_criteria" in self.knowledge_base:
            self._process_eligibility(self.knowledge_base["eligibility_criteria"])
        
        # 3. Process Application Process
        if "application_process" in self.knowledge_base:
            self._process_application(self.knowledge_base["application_process"])
        
        # 4. Process FAQs
        if "faqs" in self.knowledge_base:
            self._process_faqs(self.knowledge_base["faqs"])
        
        logger.info(f"Processed {len(self.documents)} documents from knowledge base")
        return self.documents
    
    def _process_products(self, products: Dict[str, Any]) -> None:
        """Extract product information into documents"""
        for product_id, product_info in products.items():
            name = product_info.get("name", product_id)
            description = product_info.get("description", "")
            
            # Main product document
            content = f"""
Product: {name}

Description: {description}

Rate Range: {product_info.get('rate_range', {}).get('min', 'N/A')}% - {product_info.get('rate_range', {}).get('max', 'N/A')}% APR

Term Length: {product_info.get('term_range', {}).get('min_months', 'N/A')} - {product_info.get('term_range', {}).get('max_months', 'N/A')} months
Standard: {product_info.get('term_range', {}).get('standard_months', 'N/A')} months

Credit Score Requirements:
- Minimum: {product_info.get('credit_requirements', {}).get('minimum', 'N/A')}
- Preferred: {product_info.get('credit_requirements', {}).get('preferred', 'N/A')}
- Excellent: {product_info.get('credit_requirements', {}).get('excellent', 'N/A')}

Eligible Equipment Types:
{self._format_list(product_info.get('equipment_types', []))}
            """.strip()
            
            doc = Document(
                content=content,
                metadata={
                    "source": "products",
                    "product_id": product_id,
                    "product_name": name,
                    "type": "product_overview"
                },
                doc_id=f"product_{product_id}"
            )
            self.documents.append(doc)
    
    def _process_eligibility(self, eligibility: Dict[str, Any]) -> None:
        """Extract eligibility criteria into documents"""
        
        # Credit Score Tiers
        if "credit_score_tiers" in eligibility:
            tiers = eligibility["credit_score_tiers"]
            for tier_name, tier_info in tiers.items():
                content = f"""
Credit Score Tier: {tier_name.upper()}

Score Requirement: {tier_info.get('min_score', 'N/A')} or higher

Description: {tier_info.get('description', 'N/A')}

Maximum Loan Percentage: {tier_info.get('max_loan_percentage', 'N/A')}%

Benefits: {tier_info.get('benefits', 'N/A')}
                """.strip()
                
                doc = Document(
                    content=content,
                    metadata={
                        "source": "eligibility",
                        "eligibility_type": "credit_score_tier",
                        "tier": tier_name
                    },
                    doc_id=f"eligibility_credit_tier_{tier_name}"
                )
                self.documents.append(doc)
        
        # Business Requirements
        if "business_requirements" in eligibility:
            business_reqs = eligibility["business_requirements"]
            content = f"""
Business Eligibility Requirements:

Years in Business: Minimum {business_reqs.get('min_years_in_business', 'N/A')} years

Annual Revenue: Minimum ${business_reqs.get('min_annual_revenue', 'N/A')}

Monthly Revenue: Minimum ${business_reqs.get('min_monthly_revenue', 'N/A')}

Required Documentation:
{self._format_list(business_reqs.get('required_documentation', []))}
            """.strip()
            
            doc = Document(
                content=content,
                metadata={
                    "source": "eligibility",
                    "eligibility_type": "business_requirements"
                },
                doc_id="eligibility_business_requirements"
            )
            self.documents.append(doc)
    
    def _process_application(self, app_process: Dict[str, Any]) -> None:
        """Extract application process into documents"""
        if "steps" in app_process:
            for i, step in enumerate(app_process["steps"], 1):
                content = f"""
Application Step {i}: {step.get('step_name', 'N/A')}

Duration: {step.get('duration_days', 'N/A')} days

Description: {step.get('description', 'N/A')}

Required Documents:
{self._format_list(step.get('required_documents', []))}

Key Details: {step.get('key_details', 'N/A')}
                """.strip()
                
                doc = Document(
                    content=content,
                    metadata={
                        "source": "application_process",
                        "step_number": i,
                        "step_name": step.get('step_name', 'Unknown')
                    },
                    doc_id=f"application_step_{i}"
                )
                self.documents.append(doc)
    
    def _process_faqs(self, faqs: List[Dict[str, str]]) -> None:
        """Extract FAQs into documents"""
        for i, faq in enumerate(faqs, 1):
            content = f"""
FAQ Question: {faq.get('question', 'N/A')}

Answer: {faq.get('answer', 'N/A')}

Category: {faq.get('category', 'General')}
            """.strip()
            
            doc = Document(
                content=content,
                metadata={
                    "source": "faqs",
                    "category": faq.get('category', 'General'),
                    "question": faq.get('question', 'Unknown')
                },
                doc_id=f"faq_{i}"
            )
            self.documents.append(doc)
    
    @staticmethod
    def _format_list(items: List[str]) -> str:
        """Format list items for readability"""
        if not items:
            return "None specified"
        return "\n".join([f"• {item}" for item in items])
    
    def get_documents_for_embedding(self) -> List[tuple[str, Dict]]:
        """
        Return documents in format suitable for embedding (content, metadata)
        """
        return [(doc.content, doc.metadata) for doc in self.documents]
    
    def export_documents(self, output_path: str) -> None:
        """Export processed documents to JSON for inspection"""
        output_data = [
            {
                "doc_id": doc.doc_id,
                "content": doc.content,
                "metadata": doc.metadata
            }
            for doc in self.documents
        ]
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        logger.info(f"Exported {len(self.documents)} documents to {output_path}")


def prepare_documents(kb_path: str) -> List[Document]:
    """Convenience function to process documents"""
    processor = DocumentProcessor(kb_path)
    return processor.process()


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    
    kb_path = "data/knowledge_base.json"
    processor = DocumentProcessor(kb_path)
    docs = processor.process()
    
    print(f"Processed {len(docs)} documents")
    for doc in docs[:3]:
        print(f"\n{doc.doc_id}:")
        print(doc.content[:200] + "...")
