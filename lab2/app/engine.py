from pathlib import Path
import os
import joblib

INDEX = Path(os.environ.get('INDEX_PATH', Path(__file__).resolve().parent.parent / 'index.joblib'))
class Engine:
    def __init__(self, path=INDEX):
        data=joblib.load(path)
        self.corpus_sha256=data['corpus_sha256']; self.docs=data['documents']; self.vectorizer=data['vectorizer']; self.matrix=data['matrix']
    def search(self, query, limit=3, mode='normal'):
        scores=(self.matrix @ self.vectorizer.transform([query]).T).toarray().ravel()
        order=sorted(range(len(scores)),key=lambda i:(-float(scores[i]),self.docs[i]['id']))
        if mode=='reverse': order.reverse()
        return [{'id':self.docs[i]['id'],'title':self.docs[i]['title'],'score':round(float(scores[i]),6)} for i in order[:limit]]
