from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from openai import OpenAI


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / 'data'
PROFILE_PATH = DATA_DIR / 'profile_seed.json'
SOURCE_DOCS_PATH = DATA_DIR / 'source_documents.json'
INDEX_PATH = DATA_DIR / 'kb_index.json'

SECTION_WEIGHTS = {
    'identity': 1.0,
    'professional_summary': 1.15,
    'skills': 1.18,
    'experience': 1.28,
    'education': 1.06,
    'certifications': 1.0,
    'projects': 1.34,
    'public_presence': 1.0,
    'interests': 0.92,
    'personal_profile': 0.98,
    'target_roles_and_industries': 1.0,
    'strengths_and_values': 1.02,
    'fun_facts': 0.9,
    'faq_entries': 1.15,
    'source_documents': 1.24,
    'conversation_guidelines': 0.4,
}

STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'for', 'to', 'of', 'in', 'on', 'at', 'by', 'with', 'is', 'are',
    'was', 'were', 'be', 'as', 'it', 'this', 'that', 'from', 'into', 'his', 'he', 'she', 'they', 'them',
    'about', 'what', 'which', 'who', 'how', 'when', 'where', 'why', 'can', 'does', 'do', 'did', 'has', 'have',
    'had', 'will', 'would', 'could', 'should', 'you', 'your', 'their', 'there', 'than', 'then', 'also', 'any',
}


class PersonalKnowledgeBase:
    def __init__(self, client: OpenAI, embedding_model: str) -> None:
        self.client = client
        self.embedding_model = embedding_model
        self.profile: dict[str, Any] = {}
        self.source_documents: list[dict[str, Any]] = []
        self.chunks: list[dict[str, Any]] = []

    @staticmethod
    def load_profile() -> dict[str, Any]:
        with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def load_source_documents() -> list[dict[str, Any]]:
        if not SOURCE_DOCS_PATH.exists():
            return []
        with open(SOURCE_DOCS_PATH, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        return payload.get('documents', [])

    @staticmethod
    def _chunk_long_text(text: str, chunk_size: int = 1000, overlap: int = 160) -> list[str]:
        text = re.sub(r'\s+', ' ', text).strip()
        if not text:
            return []
        if len(text) <= chunk_size:
            return [text]

        pieces: list[str] = []
        start = 0
        while start < len(text):
            end = min(len(text), start + chunk_size)
            cut = text.rfind(' ', start, end)
            if cut <= start + 180:
                cut = end
            piece = text[start:cut].strip()
            if piece:
                pieces.append(piece)
            if cut >= len(text):
                break
            start = max(0, cut - overlap)
        return pieces

    @staticmethod
    def _extract_terms(text: str) -> list[str]:
        terms = re.findall(r'[A-Za-z0-9+#.-]+', text.lower())
        return [t for t in terms if len(t) > 2 and t not in STOPWORDS]

    def build_chunks(self, profile: dict[str, Any], source_documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        chunks: list[dict[str, Any]] = []

        def add_chunk(collection: str, source_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
            clean = re.sub(r'\s+', ' ', text).strip()
            if not clean:
                return
            chunks.append(
                {
                    'collection': collection,
                    'source_id': source_id,
                    'text': clean,
                    'metadata': metadata or {},
                    'weight': SECTION_WEIGHTS.get(collection, 1.0),
                    'token_hints': self._extract_terms(clean),
                }
            )

        identity = profile.get('identity', {})
        if identity:
            identity_text = '\n'.join([f"{k.replace('_', ' ').title()}: {v}" for k, v in identity.items() if v])
            add_chunk('identity', 'identity_overview', identity_text, identity)

        for i, item in enumerate(profile.get('professional_summary', []), start=1):
            add_chunk('professional_summary', f'summary_{i}', item)

        for skill_bucket, values in profile.get('skills', {}).items():
            add_chunk(
                'skills',
                f'skills_{skill_bucket}',
                f"Skill category: {skill_bucket.replace('_', ' ').title()}\nSkills: {', '.join(values)}",
                {'skill_category': skill_bucket, 'skills': values},
            )

        for i, exp in enumerate(profile.get('experience', []), start=1):
            highlights = '\n'.join([f'- {h}' for h in exp.get('highlights', [])])
            add_chunk(
                'experience',
                f'experience_{i}',
                (
                    f"Company: {exp.get('company', '')}\n"
                    f"Role: {exp.get('role', '')}\n"
                    f"Location: {exp.get('location', '')}\n"
                    f"Duration: {exp.get('duration', '')}\n"
                    f"Highlights:\n{highlights}"
                ),
                exp,
            )

        for i, edu in enumerate(profile.get('education', []), start=1):
            add_chunk(
                'education',
                f'education_{i}',
                (
                    f"Institution: {edu.get('institution', '')}\n"
                    f"Program: {edu.get('program', '')}\n"
                    f"Status: {edu.get('status', '')}\n"
                    f"Notes: {edu.get('notes', '')}"
                ),
                edu,
            )

        for i, cert in enumerate(profile.get('certifications', []), start=1):
            add_chunk('certifications', f'certification_{i}', cert)

        for i, project in enumerate(profile.get('projects', []), start=1):
            links = project.get('links', {})
            highlights = '\n'.join([f'- {h}' for h in project.get('highlights', [])])
            add_chunk(
                'projects',
                f'project_{i}_overview',
                (
                    f"Project Name: {project.get('name', '')}\n"
                    f"Summary: {project.get('summary', '')}\n"
                    f"Problem: {project.get('problem', '')}\n"
                    f"Stack: {', '.join(project.get('stack', []))}\n"
                    f"Tags: {', '.join(project.get('tags', []))}\n"
                    f"Highlights:\n{highlights}\n"
                    + '\n'.join([f"{k.title()}: {v}" for k, v in links.items()])
                ),
                project,
            )

        for bucket in [
            'public_presence',
            'interests',
            'personal_profile',
            'target_roles_and_industries',
            'strengths_and_values',
            'fun_facts',
        ]:
            for i, item in enumerate(profile.get(bucket, []), start=1):
                add_chunk(bucket, f'{bucket}_{i}', item)

        for i, faq in enumerate(profile.get('faq_entries', []), start=1):
            add_chunk(
                'faq_entries',
                f'faq_{i}',
                f"Question: {faq.get('question', '')}\nAnswer: {faq.get('answer', '')}",
                faq,
            )

        guidelines = profile.get('conversation_guidelines', {})
        if guidelines:
            behavior = guidelines.get('behavior', [])
            add_chunk(
                'conversation_guidelines',
                'chat_behavior',
                f"Tone: {guidelines.get('tone', '')}\nBehavior:\n- " + '\n- '.join(behavior),
                guidelines,
            )

        for doc in source_documents:
            pieces = self._chunk_long_text(doc.get('text', ''))
            for idx, piece in enumerate(pieces, start=1):
                source_id = f"{doc.get('doc_id', 'doc')}_chunk_{idx}"
                metadata = {
                    'title': doc.get('title', ''),
                    'url': doc.get('url', ''),
                    'source_type': doc.get('source_type', ''),
                    'origin': doc.get('origin', ''),
                }
                add_chunk('source_documents', source_id, f"Document: {doc.get('title', '')}\n{piece}", metadata)

        return chunks

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.embedding_model, input=texts)
        return [item.embedding for item in response.data]

    def build_and_save(self) -> dict[str, Any]:
        profile = self.load_profile()
        source_documents = self.load_source_documents()
        chunks = self.build_chunks(profile, source_documents)
        embeddings = self.embed_texts([chunk['text'] for chunk in chunks])
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding

        payload = {
            'profile': profile,
            'source_documents': source_documents,
            'chunks': chunks,
            'embedding_model': self.embedding_model,
            'total_chunks': len(chunks),
        }
        with open(INDEX_PATH, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        self.profile = profile
        self.source_documents = source_documents
        self.chunks = chunks
        return payload

    def load_index(self) -> None:
        if not INDEX_PATH.exists():
            self.build_and_save()
            return
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        self.profile = payload.get('profile', {})
        self.source_documents = payload.get('source_documents', [])
        self.chunks = payload.get('chunks', [])

    @staticmethod
    def _keyword_score(query: str, text_terms: list[str]) -> float:
        q_terms = [t for t in re.findall(r'[A-Za-z0-9+#.-]+', query.lower()) if len(t) > 2 and t not in STOPWORDS]
        if not q_terms:
            return 0.0
        q_count = Counter(q_terms)
        t_count = Counter(text_terms)
        overlap = sum(min(q_count[t], t_count[t]) for t in q_count)
        return overlap / max(1, len(q_terms))

    def retrieve(self, query: str, allowed_collections: list[str] | None = None, top_k: int = 8) -> list[dict[str, Any]]:
        if not self.chunks:
            self.load_index()

        query_embedding = np.array(self.embed_texts([query])[0], dtype=np.float32)
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            return []

        results: list[dict[str, Any]] = []
        for chunk in self.chunks:
            collection = chunk.get('collection', '')
            if allowed_collections and collection not in allowed_collections:
                continue

            vector = np.array(chunk['embedding'], dtype=np.float32)
            denom = np.linalg.norm(vector) * query_norm
            semantic = float(np.dot(vector, query_embedding) / denom) if denom else 0.0
            lexical = self._keyword_score(query, chunk.get('token_hints', []))
            blended = (semantic * 0.82) + (lexical * 0.18)
            weighted_score = blended * float(chunk.get('weight', 1.0))

            enriched = dict(chunk)
            enriched['semantic_score'] = round(semantic, 4)
            enriched['lexical_score'] = round(lexical, 4)
            enriched['score'] = round(blended, 4)
            enriched['weighted_score'] = round(weighted_score, 4)
            results.append(enriched)

        results.sort(key=lambda x: x['weighted_score'], reverse=True)
        return results[:top_k]
