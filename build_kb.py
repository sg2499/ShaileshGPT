from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from knowledge_base import PersonalKnowledgeBase
from prepare_sources import main as prepare_sources_main


ROOT = Path(__file__).resolve().parent


def main() -> None:
    load_dotenv(ROOT / '.env', override=True)
    prepare_sources_main()
    embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    client = OpenAI()
    kb = PersonalKnowledgeBase(client, embedding_model)
    payload = kb.build_and_save()
    print(f"Knowledge base built successfully with {payload['total_chunks']} chunks.")
    print(f"Embedding model: {payload['embedding_model']}")
    print(f"Source documents: {len(payload.get('source_documents', []))}")


if __name__ == '__main__':
    main()
