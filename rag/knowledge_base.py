import os
import json
import chromadb
from chromadb.utils import embedding_functions

class KnowledgeBase:
    def __init__(self, db_path="./rag_db"):
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path)
        # Default embedding function (sentence-transformers/all-MiniLM-L6-v2)
        # Downloads ~23MB on first use
        self.embed_fn = embedding_functions.DefaultEmbeddingFunction()

    def get_or_create_collection(self, name):
        return self.client.get_or_create_collection(
            name=name, 
            embedding_function=self.embed_fn
        )

    def index_all(self, data_dir="./bible_data"):
        print(f"[*] Starting indexing from {data_dir}...")
        
        # 1. Index Jewish Culture
        jewish_file = os.path.join(data_dir, "jewish_culture.json")
        if os.path.exists(jewish_file):
            col = self.get_or_create_collection("jewish_culture")
            with open(jewish_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                ids = [item["id"] for item in data]
                docs = [f"{item['title']}\n{item['content']}" for item in data]
                metas = [{"category": item["category"], "period": item["period"]} for item in data]
                col.add(ids=ids, documents=docs, metadatas=metas)
            print(f"[+] Indexed {len(data)} Jewish culture items.")

        # 2. Index Greek Culture
        greek_file = os.path.join(data_dir, "greek_culture.json")
        if os.path.exists(greek_file):
            col = self.get_or_create_collection("greek_culture")
            with open(greek_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                ids = [item["id"] for item in data]
                docs = [f"{item['title']}\n{item['content']}" for item in data]
                metas = [{"category": item["category"], "period": item["period"]} for item in data]
                col.add(ids=ids, documents=docs, metadatas=metas)
            print(f"[+] Indexed {len(data)} Greek culture items.")

        # 3. Index Key Verses
        verses_file = os.path.join(data_dir, "key_verses.json")
        if os.path.exists(verses_file):
            col = self.get_or_create_collection("verses")
            with open(verses_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                ids = [item["reference"] for item in data]
                docs = [f"{item['reference']}: {item['text']}" for item in data]
                metas = [{"themes": ",".join(item["themes"]), "testament": item["testament"]} for item in data]
                col.add(ids=ids, documents=docs, metadatas=metas)
            print(f"[+] Indexed {len(data)} key verses.")

        # 4. Index Commentary
        commentary_file = os.path.join(data_dir, "commentary_notes.json")
        if os.path.exists(commentary_file):
            col = self.get_or_create_collection("commentary")
            with open(commentary_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                ids = [f"comm_{i}" for i in range(len(data))]
                docs = [f"Ref: {item['reference']} | Tradition: {item['tradition']} | Topic: {item['topic']}\n{item['note']}" for item in data]
                metas = [{"reference": item["reference"], "tradition": item["tradition"]} for item in data]
                col.add(ids=ids, documents=docs, metadatas=metas)
            print(f"[+] Indexed {len(data)} commentary notes.")

        print("[*] Indexing complete.")

    def is_indexed(self):
        try:
            return len(self.client.list_collections()) >= 4
        except:
            return False
