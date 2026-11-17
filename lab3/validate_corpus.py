"""Validate the supplied corpus before indexing; no network access required."""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path

path = Path(os.getenv('CORPUS_PATH', str(Path(__file__).with_name('corpus.json'))))
raw = path.read_bytes()
def unique_object(pairs):
    data = {}
    for key, value in pairs:
        if key in data: raise ValueError(f'duplicate field: {key}')
        data[key] = value
    return data
corpus = json.loads(raw, object_pairs_hook=unique_object)
docs = []
errors = []
for section in corpus['sections']:
    for subsection in section['subsections']:
        for doc in subsection['documents']:
            docs.append(doc)
            key = f"{doc.get('id')}@{doc.get('version')}"
            if doc.get('path') != [section['title'], subsection['title']]: errors.append(f'{key}: invalid path')
            if doc.get('status') not in {'Действует', 'Архив', 'Черновик'}: errors.append(f'{key}: invalid status')
            if doc.get('visibility') not in {'cloud_ok', 'local_only'}: errors.append(f'{key}: invalid visibility')
            try: datetime.date.fromisoformat(doc['date'])
            except (KeyError, ValueError): errors.append(f'{key}: invalid date')
            anchors = [s.get('anchor') for s in doc.get('sections', [])]
            if not anchors or None in anchors or len(anchors) != len(set(anchors)): errors.append(f'{key}: invalid anchors')
keys = [f"{d['id']}@{d['version']}" for d in docs]
if len(keys) != len(set(keys)): errors.append('duplicate ID/version')
active = collections.Counter(d['id'] for d in docs if d['status'] == 'Действует')
errors += [f'{k}: multiple active versions' for k, n in active.items() if n > 1]
for doc in docs:
    for link in doc['links'] + ([doc['replaces']] if doc.get('replaces') else []):
        if link not in keys: errors.append(f"{doc['id']}@{doc['version']}: unresolved reference {link}")
print(f'SHA-256: {hashlib.sha256(raw).hexdigest()}')
print(f"Records: {len(docs)}; unique IDs: {len(set(d['id'] for d in docs))}; sections: {len(corpus['sections'])}; subsections: {sum(len(s['subsections']) for s in corpus['sections'])}")
print('Statuses:', dict(collections.Counter(d['status'] for d in docs)))
print('Visibility:', dict(collections.Counter(d['visibility'] for d in docs)))
print('Validation errors:', len(errors))
for error in errors: print('-', error)
if errors: raise SystemExit(1)
