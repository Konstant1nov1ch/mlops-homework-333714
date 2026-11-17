import argparse,json,urllib.request
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('url'); a=p.parse_args()
cases=json.loads((Path(__file__).parent/'data/eval.json').read_text()); reciprocal=[]
for case in cases:
    request=urllib.request.Request(a.url.rstrip('/')+'/search',data=json.dumps({'query':case['query'],'limit':3}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=10) as response: ids=[r['id'] for r in json.load(response)['results']]
    rank=ids.index(case['relevant'])+1 if case['relevant'] in ids else 0
    reciprocal.append(1/rank if rank else 0)
mrr=sum(reciprocal)/len(reciprocal); recall=sum(bool(r) for r in reciprocal)/len(reciprocal)
print(json.dumps({'mrr':round(mrr,4),'recall_at_3':round(recall,4)}))
raise SystemExit(0 if mrr>=.85 and recall>=.90 else 1)
