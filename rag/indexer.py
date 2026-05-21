import sys
import os

# Add the parent directory to sys.path so we can import the rag module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.knowledge_base import KnowledgeBase

def run_indexing():
    kb = KnowledgeBase()
    kb.index_all()

if __name__ == "__main__":
    run_indexing()
