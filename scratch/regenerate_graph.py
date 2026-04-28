from src.knowledge.graph_store import GraphStore
from src.knowledge.graph_reporter import GraphReporter
import os

def migrate_and_regenerate():
    store = GraphStore()
    if store.load_from_disk():
        print("Graph data loaded successfully.")
        reporter = GraphReporter()
        html_path = reporter.generate_interactive_html(store)
        print(f"Graph HTML regenerated at: {html_path}")
    else:
        print("Failed to load graph data.")

if __name__ == "__main__":
    migrate_and_regenerate()
