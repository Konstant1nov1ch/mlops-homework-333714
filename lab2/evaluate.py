import argparse, json
from pathlib import Path
from app.engine import Engine
p=argparse.ArgumentParser(); p.add_argument('--mode',choices=['normal','reverse'],default='normal'); a=p.parse_args()
cases=json.loads((Path(__file__).parent/'data/eval.json').read_text()); e=Engine(); rr=[]
for case in cases:
    ids=[x['id'] for x in e.search(case['query'],3,a.mode)]
    rank=ids.index(case['relevant'])+1 if case['relevant'] in ids else 0
    rr.append(1/rank if rank else 0)
mrr=sum(rr)/len(rr); recall=sum(x>0 for x in rr)/len(rr)
print(json.dumps({'mode':a.mode,'queries':len(rr),'mrr':round(mrr,4),'recall_at_3':round(recall,4),'passed':mrr>=.85 and recall>=.90}))
raise SystemExit(0 if mrr>=.85 and recall>=.90 else 1)
