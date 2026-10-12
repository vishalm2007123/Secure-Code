import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "online"
    print("[OK] GET / passed")

def test_presets():
    response = client.get("/presets")
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) >= 5
    print(f"[OK] GET /presets passed ({len(presets)} presets available)")

def test_analyze():
    code = "import os\ncmd = input('cmd: ')\nos.system(cmd)"
    response = client.post("/analyze", json={"code": code, "language": "Python"})
    assert response.status_code == 200
    data = response.json()
    assert data["vulnerable"] is True
    assert data["security_score"] < 100
    assert len(data["findings"]) > 0
    print(f"[OK] POST /analyze passed (Score: {data['security_score']}, Findings: {len(data['findings'])})")

def test_training_endpoints():
    res_status = client.get("/train/status")
    assert res_status.status_code == 200
    print("[OK] GET /train/status passed")

    res_models = client.get("/models/list")
    assert res_models.status_code == 200
    assert len(res_models.json()) >= 2
    print(f"[OK] GET /models/list passed ({len(res_models.json())} models listed)")

    res_train = client.post("/train/start", json={"epochs": 2, "learning_rate": 0.0002})
    assert res_train.status_code == 200
    assert res_train.json()["status"] == "success"
    print(f"[OK] POST /train/start passed (Job ID: {res_train.json()['job_id']})")

def test_analytics_and_catalog():
    res_analytics = client.get("/analytics/stats")
    assert res_analytics.status_code == 200
    data_a = res_analytics.json()
    assert "dataset" in data_a
    assert data_a["dataset"]["clean_records"] > 0
    print(f"[OK] GET /analytics/stats passed ({data_a['dataset']['clean_records']} records reported)")

    res_catalog = client.get("/rules/catalog")
    assert res_catalog.status_code == 200
    catalog = res_catalog.json()
    assert len(catalog) >= 5
    print(f"[OK] GET /rules/catalog passed ({len(catalog)} rules cataloged)")

if __name__ == "__main__":
    test_root()
    test_presets()
    test_analyze()
    test_training_endpoints()
    test_analytics_and_catalog()
    print("\nAll API integration, training, and analytics tests passed successfully!")


