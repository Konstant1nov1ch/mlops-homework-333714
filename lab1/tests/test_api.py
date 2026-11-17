from fastapi.testclient import TestClient
from app.main import app

def test_iris_predictions_and_validation():
    with TestClient(app) as client:
        assert client.get('/health').json()['status']=='ready'
        for vector, expected in [([5.1,3.5,1.4,0.2],0),([6.3,3.3,6.0,2.5],2)]:
            assert client.post('/predict',json={'features':vector}).json()['class_id']==expected
        assert client.post('/predict',json={'features':[1,2]}).status_code==422
