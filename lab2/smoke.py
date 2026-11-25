"""Evaluate the live search endpoint against the supplied relevance judgments."""
import argparse
import json
import urllib.request
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('url')
args = parser.parse_args()
cases = json.loads((Path(__file__).parent / 'data/eval.json').read_text())
reciprocal = []
for case in cases:
    request = urllib.request.Request(
        args.url.rstrip('/') + '/v1/search',
        data=json.dumps({'query': case['query'], 'limit': 3}).encode(),
        headers={'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        ids = [item['id'] for item in json.load(response)['results']]
    ranks = [ids.index(doc_id) + 1 for doc_id in case['relevant'] if doc_id in ids]
    reciprocal.append(1 / min(ranks) if ranks else 0)
mrr = sum(reciprocal) / len(reciprocal)
recall = sum(rank > 0 for rank in reciprocal) / len(reciprocal)
print(json.dumps({'mrr': round(mrr, 4), 'recall_at_3': round(recall, 4)}))
raise SystemExit(0 if mrr >= 0.85 and recall >= 0.90 else 1)
