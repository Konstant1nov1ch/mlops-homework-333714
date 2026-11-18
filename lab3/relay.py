"""Optional localhost-operated relay for a cluster without outbound HTTPS."""
import asyncio, hmac, os, uuid
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, Response

app=FastAPI()
worker_key=os.environ['RELAY_WORKER_KEY']
cloud_key=os.environ['LLM7_API_KEY']
queue=asyncio.Queue(maxsize=4)
pending={}

def authorize(value, expected):
    if not value or not hmac.compare_digest(value,expected):
        raise HTTPException(401,'unauthorized')

@app.get('/health')
async def health(): return {'status':'ready'}

@app.post('/v1/chat/completions')
async def completion(request: Request, authorization: str | None = Header(default=None)):
    authorize(authorization, 'Bearer '+cloud_key)
    if int(request.headers.get('content-length','0'))>100_000: raise HTTPException(413,'request too large')
    payload=await request.json()
    request_id=uuid.uuid4().hex; future=asyncio.get_running_loop().create_future();pending[request_id]=future
    try:
        try: queue.put_nowait((request_id,payload))
        except asyncio.QueueFull: raise HTTPException(503,'relay busy')
        try: result=await asyncio.wait_for(asyncio.shield(future),timeout=24)
        except TimeoutError: raise HTTPException(504,'relay worker unavailable')
        headers={}
        if result.get('retry_after'): headers['Retry-After']=str(result['retry_after'])[:100]
        return JSONResponse(result['body'],status_code=result['status'],headers=headers)
    finally:
        pending.pop(request_id,None)
        if not future.done(): future.cancel()

@app.get('/worker/next')
async def next_job(x_relay_key: str | None = Header(default=None)):
    authorize(x_relay_key,worker_key)
    while True:
        try: request_id,payload=await asyncio.wait_for(queue.get(),timeout=20)
        except TimeoutError: return Response(status_code=204)
        if request_id in pending:return {'id':request_id,'payload':payload}

@app.post('/worker/result')
async def complete(request:Request,x_relay_key: str | None = Header(default=None)):
    authorize(x_relay_key,worker_key)
    result=await request.json();future=pending.get(result.get('id'))
    if not future or future.done(): raise HTTPException(404,'request expired')
    code=result.get('status');body=result.get('body')
    if not isinstance(code,int) or not 100<=code<=599 or not isinstance(body,dict): raise HTTPException(400,'invalid response')
    future.set_result({'status':code,'body':body,'retry_after':result.get('retry_after')})
    return {'accepted':True}
