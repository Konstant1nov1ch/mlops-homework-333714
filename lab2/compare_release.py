import json, os, sys, urllib.request

def get(url):
    with urllib.request.urlopen(url.rstrip('/')+'/meta', timeout=10) as r: return json.load(r)
staging, production = map(get, sys.argv[1:3])
expected=os.environ['IMAGE_DIGEST']
assert staging['image_digest']==production['image_digest']==expected, 'different digest'
assert staging['corpus_sha256']==production['corpus_sha256'], 'different index corpus'
assert staging['ranking_mode']==production['ranking_mode']=='normal', 'bad ranking mode'
assert staging['environment']=='staging' and production['environment']=='production', 'bad environment'
print(json.dumps({'status':'passed','digest':expected,'corpus_sha256':staging['corpus_sha256']}))
