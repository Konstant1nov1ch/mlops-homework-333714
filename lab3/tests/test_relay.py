import asyncio, importlib, os
import httpx

def test_relay_auth_and_roundtrip(monkeypatch):
    monkeypatch.setenv('RELAY_WORKER_KEY','worker-test-key')
    monkeypatch.setenv('LLM7_API_KEY','cloud-test-key')
    import relay
    importlib.reload(relay)
    async def exercise():
        transport=httpx.ASGITransport(app=relay.app)
        async with httpx.AsyncClient(transport=transport,base_url='http://test') as client:
            assert (await client.get('/worker/next')).status_code==401
            assert (await client.post('/v1/chat/completions',json={})).status_code==401
            pending=asyncio.create_task(client.post('/v1/chat/completions',headers={'Authorization':'Bearer cloud-test-key'},json={'messages':[{'role':'user','content':'synthetic'}]}))
            job=(await client.get('/worker/next',headers={'X-Relay-Key':'worker-test-key'})).json()
            assert job['payload']['messages'][0]['content']=='synthetic'
            accepted=await client.post('/worker/result',headers={'X-Relay-Key':'worker-test-key'},json={'id':job['id'],'status':429,'body':{'error':'synthetic'},'retry_after':'7'})
            result=await pending
            assert accepted.status_code==200 and result.status_code==429 and result.headers['Retry-After']=='7'
    asyncio.run(exercise())
