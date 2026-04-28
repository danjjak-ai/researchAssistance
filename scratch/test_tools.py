from src.tools.arxiv_tool import search_arxiv, download_pdf
from src.knowledge.graph_store import GraphStore
from src.knowledge.entity_extractor import extract_entities_and_relations
from src.knowledge.graph_reporter import GraphReporter
import os

def test_flow():
    query = "Structure of small language models"
    print(f"Searching ArXiv for: {query}")
    results = search_arxiv.invoke({"query": query, "max_results": 2})
    print(f"Found {len(results)} papers.")
    
    if results:
        arxiv_id = results[0]['arxiv_id']
        print(f"Downloading {arxiv_id}...")
        path = download_pdf(arxiv_id)
        print(f"Downloaded to {path}")
        
        mock_text = f"Research on {results[0]['title']}. Key concept: SLM (Small Language Model). It uses Transformer architecture."
        print("Extracting entities...")
        data = extract_entities_and_relations(mock_text)
        print(f"Extracted: {data}")
        
        store = GraphStore()
        store.load_from_disk()
        store.add_entities_and_relations(data)
        
        # Add a test paper node with PDF path
        store.graph.add_node("2603.21389v1", type="Paper", pdf_path="vault/raw/2603.21389v1.pdf")
        store.graph.add_edge("2603.21389v1", "SLM", type="defines")
        
        store.save_to_disk()
        
        reporter = GraphReporter()
        html = reporter.generate_interactive_html(store)
        print(f"Graph generated at {html}")

if __name__ == "__main__":
    test_flow()
