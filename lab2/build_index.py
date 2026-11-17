import json, hashlib
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
root=Path(__file__).resolve().parent
docs=json.loads((root/'data/documents.json').read_text())
assert len({d['id'] for d in docs})==len(docs)
v=TfidfVectorizer(analyzer='char_wb',ngram_range=(2,5),lowercase=True,sublinear_tf=True)
m=v.fit_transform([d['title']+' '+d['text'] for d in docs])
joblib.dump({'documents':docs,'vectorizer':v,'matrix':m,'corpus_sha256':hashlib.sha256((root/'data/documents.json').read_bytes()).hexdigest()},root/'index.joblib',compress=3)
print('Indexed',len(docs),'documents')
