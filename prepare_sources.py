from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / 'data'
RAW_DIR = DATA_DIR / 'raw'
BLUEPRINT_PATH = DATA_DIR / 'public_sources_blueprint.json'
OUTPUT_PATH = DATA_DIR / 'source_documents.json'


def clean_text(text: str) -> str:
    text = text.replace('\x00', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def pdf_to_text(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ''
        if text.strip():
            pages.append(clean_text(text))
    return '\n\n'.join(pages)


def main() -> None:
    documents: list[dict[str, Any]] = []

    if BLUEPRINT_PATH.exists():
        payload = json.loads(BLUEPRINT_PATH.read_text(encoding='utf-8'))
        documents.extend(payload.get('documents', []))

    raw_specs = [
        {
            'doc_id': 'resume_pdf_raw',
            'title': 'Resume PDF — Raw Extract',
            'source_type': 'pdf',
            'origin': 'uploaded_resume',
            'path': RAW_DIR / 'shailesh_resume.pdf',
        },
        {
            'doc_id': 'linkedin_profile_pdf_raw',
            'title': 'LinkedIn Profile PDF — Raw Extract',
            'source_type': 'pdf',
            'origin': 'uploaded_profile_pdf',
            'path': RAW_DIR / 'linkedin_profile.pdf',
        },
    ]

    for spec in raw_specs:
        path = spec['path']
        if path.exists():
            documents.append(
                {
                    'doc_id': spec['doc_id'],
                    'title': spec['title'],
                    'source_type': spec['source_type'],
                    'origin': spec['origin'],
                    'url': '',
                    'text': pdf_to_text(path),
                }
            )

    OUTPUT_PATH.write_text(json.dumps({'documents': documents}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Prepared {len(documents)} source documents at {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
