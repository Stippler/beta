from fastapi.testclient import TestClient
from api import app  # Import your FastAPI app

client = TestClient(app)

def test_analyze_text_list():
    request_data = {"texts": ["Today I want to go for a walk at 10 am in a park that is 5 minutes away from my home in Kosice", "Today I want to go for a 1-hour walk at 10 am in a park that is 5 minutes away from my home in Kosice"]}
    response = client.post("/text_list/", json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    print(response_data)
