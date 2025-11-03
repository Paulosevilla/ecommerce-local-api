
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_list_update_product():
    payload = {'name':'Miel de apiario','description':'Miel pura','price':'25.50','stock':10,'category':'Alimentos'}
    r = client.post('/products/', json=payload)
    assert r.status_code == 201, r.text
    prod = r.json()
    pid = prod['id']
    # list
    r2 = client.get('/products/')
    assert r2.status_code == 200
    # update
    r3 = client.put(f'/products/{pid}', json={'stock': 15})
    assert r3.status_code == 200
    assert r3.json()['stock'] == 15
