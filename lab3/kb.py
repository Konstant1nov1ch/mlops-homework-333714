import json, re, sqlite3
from pathlib import Path
from index import CORPUS, INDEX, normalize
from safety import unsafe_fragment

def list_sections():
    data=json.loads(CORPUS.read_text())
    return [{'title':s['title'],'subsections':[{'title':sub['title'],'documents':[{'id':d['id'],'version':d['version'],'title':d['title'],'status':d['status']} for d in sub['documents']]} for sub in s['subsections']]} for s in data['sections']]

def get_doc(doc_id,version):
    for section in json.loads(CORPUS.read_text())['sections']:
        for sub in section['subsections']:
            for d in sub['documents']:
                if d['id']==doc_id and d['version']==version: return d
    return None

def search_docs(query, statuses=None, path=None, version=None, limit=5):
    statuses=statuses or ['Действует']; limit=max(1,min(int(limit),5))
    allowed={'Действует','Архив','Черновик'}
    if not set(statuses)<=allowed: raise ValueError('Unknown status')
    stop = set(normalize('ли откуда взялось число запущены кто сколько какой какая как почему что это для при из на по и в с до за или').split())
    terms=[t for t in dict.fromkeys(normalize(query).split()) if t not in stop]
    if not terms: return []
    exact_ids={x.upper() for x in re.findall(r'\b[A-Z]-\d{2}\b',query,re.I)}
    exact_codes={x.lower() for x in re.findall(r'\b[a-z][a-z0-9]*_[a-z0-9_]+\b',query,re.I)}
    expression=' OR '.join('"'+t.replace('"','""')+'"' for t in terms)
    filters=['search MATCH ?', 'c.status IN ('+','.join('?' for _ in statuses)+')']; args=[expression,*statuses]
    if path: filters.append('c.path = ?'); args.append(path)
    if version: filters.append('c.version = ?'); args.append(version)
    with sqlite3.connect(f'file:{INDEX}?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        rows=db.execute('SELECT c.*, bm25(search) AS score FROM search JOIN chunks c ON c.id=search.rowid WHERE '+' AND '.join(filters)+' ORDER BY score LIMIT 100',args).fetchall()
        result=[]; seen=set()
        for row in rows:
            if unsafe_fragment(row['body']): continue
            key=(row['doc_id'],row['version'])
            if key not in seen: result.append(dict(row)); seen.add(key)
        if result:
            best=result[0]
            linked=set((get_doc(best['doc_id'],best['version']) or {}).get('links',[]))
            section=best['path'].split(' / ')[0]
            result.sort(key=lambda item:(item['score']-(100.0 if item['doc_id'].upper() in exact_ids else 0.0)-(50.0 if any(code in item['body'].lower() for code in exact_codes) else 0.0)-(1.0 if f"{item['doc_id']}@{item['version']}" in linked else 0.0)-(0.6 if item['path'].split(' / ')[0]==section else 0.0),item['doc_id'],item['version']))
        return result[:limit]
