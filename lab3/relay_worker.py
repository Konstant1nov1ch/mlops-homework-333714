"""Run on the student's computer while kubectl forwards the relay service."""
import asyncio,os
from pathlib import Path
import httpx

def read_llm7():
    file=Path(os.environ.get('LLM7_ENV_FILE',str(Path.home()/'Developer/DevOpsLLM/.env.dev')))
    for line in file.read_text().splitlines():
        if line.strip().startswith('TOKEN') and '=' in line:
            value=line.split('=',1)[1].strip().strip('"\'')
            return value[7:].strip() if value.lower().startswith('bearer ') else value
    raise RuntimeError('TOKEN not found')
async def main():
    secret=Path(os.environ['RELAY_KEY_FILE']).read_text().strip(); token=read_llm7()
    relay=os.getenv('RELAY_URL','http://127.0.0.1:18100').rstrip('/')
    async with httpx.AsyncClient(timeout=25) as client:
        print('Relay worker started; no request text is logged.',flush=True)
        while True:
            try:
                task=await client.get(relay+'/worker/next',headers={'X-Relay-Key':secret})
                if task.status_code==204:continue
                task.raise_for_status(); job=task.json()
                try:
                    response=await client.post('https://api.llm7.io/v1/chat/completions',headers={'Authorization':'Bearer '+token},json=job['payload'],timeout=20)
                    try:body=response.json()
                    except ValueError:body={'error':{'message':'invalid upstream response'}}
                    result={'id':job['id'],'status':response.status_code,'body':body,'retry_after':response.headers.get('Retry-After')}
                except httpx.TimeoutException:result={'id':job['id'],'status':504,'body':{'error':{'message':'upstream timeout'}}}
                except httpx.HTTPError:result={'id':job['id'],'status':502,'body':{'error':{'message':'upstream unavailable'}}}
                await client.post(relay+'/worker/result',headers={'X-Relay-Key':secret},json=result)
            except (httpx.HTTPError,ValueError,KeyError):
                await asyncio.sleep(2)
if __name__=='__main__':asyncio.run(main())
