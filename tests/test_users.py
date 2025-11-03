
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_and_get_user():
    resp = client.post('/users/', json={'name': 'Ana', 'email': 'ana@example.com', 'password': 'secret12'})
    assert resp.status_code == 201
    user = resp.json()
    uid = user['id']
    # add address
    addr = {'street': 'Av. Libertad', 'city': 'Cochabamba'}
    resp2 = client.post(f'/users/{uid}/addresses', json=addr)
    assert resp2.status_code == 200
    # get
    resp3 = client.get(f'/users/{uid}')
    assert resp3.status_code == 200
    data = resp3.json()
    assert data['addresses'][0]['city'] == 'Cochabamba'
