from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_violations_pagination():
    response = client.get("/api/v1/violations?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert data["page"] == 1

def test_create_employee_invalid_file():
    files = {'photo': ('test.txt', b'text', 'text/plain')}
    data = {'name': 'Felix', 'department': 'AI'}
    response = client.post("/api/v1/employees/", data=data, files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "File harus berupa gambar."