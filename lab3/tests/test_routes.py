import asyncio
import httpx
from fastapi.testclient import TestClient
import portal

def test_fallback_preserves_context_and_cloud_recovery(monkeypatch):
    cards=[{'doc_id':'M-05','version':'2.0','title':'Каналы','status':'Действует','visibility':'cloud_ok','anchor':'s01','body':'Предел — 5000.'}]
    calls=[]; cloud_fails=True
    async def fake_tool(name,args): return cards
    async def fake_model(base,key,model,messages,timeout):
        calls.append((base,messages))
        if base==portal.cloud_url and cloud_fails:
            request=httpx.Request('POST',base); response=httpx.Response(429,request=request,headers={'Retry-After':'1'})
            raise httpx.HTTPStatusError('limited',request=request,response=response)
        return 'Предел — 5000 [1].'
    monkeypatch.setattr(portal,'tool',fake_tool); monkeypatch.setattr(portal,'call_model',fake_model); monkeypatch.setattr(portal,'cloud_key','test-only')
    portal.state.update(until=0.0,probing=False)
    with TestClient(portal.app) as client:
        r=client.post('/api/ask',json={'query':'Какой предел?'}).json()
        assert r['route']=='local' and r['reason']=='rate_limit'
        assert calls[0][1]==calls[1][1]
        cloud_fails=False; portal.state['until']=0
        assert client.post('/api/ask',json={'query':'Какой предел?'}).json()['route']=='cloud'
        prior=len(calls)
        assert client.post('/api/ask',json={'query':'Какой предел?','private':True}).json()['route']=='local'
        assert all(c[0]!=portal.cloud_url for c in calls[prior:])

def test_invalid_citation_is_search_only(monkeypatch):
    async def fake_tool(name,args): return [{'doc_id':'A','version':'1','title':'x','status':'Действует','visibility':'local_only','anchor':'s01','body':'fact'}]
    async def fake_model(*args): return 'Выдумано [9]'
    monkeypatch.setattr(portal,'tool',fake_tool); monkeypatch.setattr(portal,'call_model',fake_model)
    with TestClient(portal.app) as client:
        r=client.post('/api/ask',json={'query':'Что известно?'}).json()
        assert r['route']=='search_only' and r['answer']==''
