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
    result_data = response_data["result"]
    print(result_data)
    assert "title" in result_data
    assert "activity" in result_data
    assert result_data["date"] == "06/04/2024"
    assert result_data["from"] == "10:00"
    assert result_data["to"] == "11:00"
    assert "location_text" in result_data
    assert "location_gps" in result_data
    assert result_data["sheltered"] is False  # Depending on what you expect
