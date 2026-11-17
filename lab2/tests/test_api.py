from fastapi.testclient import TestClient
from app.main import app

def test_search_contract():
    with TestClient(app) as client:
        assert client.get('/ready').json()['status']=='ready'
        result=client.post('/search',json={'query':'как откатить неудачный релиз модели','limit':3})
        assert result.status_code==200
        assert result.json()['results'][0]['id']=='rollback'
        assert client.post('/search',json={'query':'','limit':3}).status_code==422
        assert client.post('/search',json={'query':'тест','limit':100}).status_code==422
