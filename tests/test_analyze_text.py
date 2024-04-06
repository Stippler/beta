from fastapi.testclient import TestClient
from api import app  # Import your FastAPI app

client = TestClient(app)

def test_analyze_text():
    request_data = {"text": "Today I want to go for a 1-hour walk at 10 am in a park that is 5 minutes away from my home in Kosice"}
    response = client.post("/text/", json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert "result" in response_data
    print(response.json()) 
