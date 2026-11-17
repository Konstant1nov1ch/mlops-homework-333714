import os
import sqlite3
from starlette.responses import JSONResponse
from mcp.server.fastmcp import FastMCP
import kb
mcp = FastMCP('line-kb', host=os.getenv('HOST', '127.0.0.1'), port=int(os.getenv('PORT', '18081')), stateless_http=True)
@mcp.custom_route('/health', methods=['GET'])
async def health(request):
    try:
        with sqlite3.connect(f'file:{kb.INDEX}?mode=ro', uri=True) as db:
            db.execute('SELECT digest FROM meta').fetchone()
        return JSONResponse({'status': 'ready'})
    except sqlite3.Error:
        return JSONResponse({'status': 'not_ready'}, status_code=503)
@mcp.tool()
def search_docs(query: str, statuses: list[str] | None = None, path: str | None = None, version: str | None = None) -> list[dict]:
    """Search document sections. Default status is Действует; pass Архив or Черновик explicitly."""
    return kb.search_docs(query, statuses, path, version)
@mcp.tool()
def get_doc(doc_id: str, version: str) -> dict:
    """Get an exact document revision."""
    doc=kb.get_doc(doc_id,version)
    if doc is None: raise ValueError('Document revision not found')
    return doc
@mcp.tool()
def list_sections() -> list[dict]:
    """List document hierarchy and revisions."""
    return kb.list_sections()
if __name__ == '__main__': mcp.run(transport='streamable-http')
