import os
os.environ["OMNIFORGE_DATA"] = "test_omniforge_data"

import pytest
from fastapi.testclient import TestClient
from omniforge.backend.main import app
import shutil

client = TestClient(app)

# Setup/Teardown for a clean test environment
@pytest.fixture(autouse=True)
def setup_test_env():
    test_data_dir = "test_omniforge_data"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir)
    os.environ["OMNIFORGE_DATA"] = test_data_dir
    yield
    # Cleanup after tests
    # shutil.rmtree(test_data_dir)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_project_lifecycle():
    # 1. Create Project
    response = client.post("/api/projects", json={"project_name": "Test Project"})
    assert response.status_code == 201
    project_id = response.json()["id"]
    
    # 2. List Projects
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert any(p["id"] == project_id for p in response.json())

    # 3. Add Asset
    response = client.post(f"/api/projects/{project_id}/assets", json={
        "name": "Test Sprite",
        "type": "spritesheet",
        "category": "character",
        "file_path": "sprites/hero.png",
        "tags": ["test", "hero"]
    })
    assert response.status_code == 201
    asset_id = response.json()["asset"]["id"]

    # 4. Get Asset
    response = client.get(f"/api/projects/{project_id}/assets")
    assert response.status_code == 200
    assert any(a["id"] == asset_id for a in response.json())

def test_quality_analysis_mock():
    # Create project and asset first
    res_p = client.post("/api/projects", json={"project_name": "qtest"})
    p_id = res_p.json()["id"]
    
    # Create a real 1x1 PNG file
    import base64
    one_pixel_png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")
    os.makedirs(f"test_omniforge_data/projects/{p_id}/sprites", exist_ok=True)
    with open(f"test_omniforge_data/projects/{p_id}/sprites/test.png", "wb") as f:
        f.write(one_pixel_png)
        
    res_a = client.post(f"/api/projects/{p_id}/assets", json={
        "name": "A1", "type": "image", "category": "character", "file_path": "sprites/test.png"
    })
    a_id = res_a.json()["asset"]["id"]

    response = client.get(f"/api/quality/{p_id}/{a_id}/analyze")
    assert response.status_code == 200
    assert "score" in response.json()
