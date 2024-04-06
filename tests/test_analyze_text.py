from fastapi.testclient import TestClient
from api2 import app  # Import your FastAPI app

client = TestClient(app)

def simple_promt():
    request_data = {"text": "Today I want to go for a 1-hour walk at 10 am in a park that is 5 minutes away from my home in Kosice"}
    response = client.post("/text/", json=request_data)
    assert response.status_code == 200
    print(response.json()) 

def more_complex_promt():
    request_data = {"text": "next year in march in want to plant crpos. They should be larger than my neighbours. I want to plant them in the field behind my house."}
    response = client.post("/text/", json=request_data)
    assert response.status_code == 200
    print(response.json())