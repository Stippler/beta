from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, List, Optional 

app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Models
class Task(BaseModel):
    title: str
    timeframe: str
    location: str

class WeatherRequest(BaseModel):
    longitude: float
    latitude: float
    timeframe: str

class TextRequest(BaseModel):
    text: str

# In-memory storage
tasks = []
weather_data = []  # Placeholder for weather data

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# Endpoints
@app.post("/task/")
async def create_task(task: Task):
    tasks.append(task)
    # Placeholder for logic to determine if task is well placed
    # For now, returns "yes" by default
    return {"result": "yes"}

@app.get("/task/")
async def list_tasks():
    return tasks

@app.post("/text/")
async def analyze_text(text_request: TextRequest):
    # Placeholder for natural text analysis
    # For now, returns "yes" by default
    return {"result": "yes"}

@app.post("/weather/")
async def get_weather(weather_request: WeatherRequest):
    # Placeholder for fetching weather data based on location and timeframe
    # You should replace this with a call to a real weather API
    # For demonstration, it returns an empty list
    return weather_data

@app.post("/ok/")
async def check_weather_ok(weather_request: WeatherRequest):
    # Placeholder for logic to determine if weather is OK for an event
    # This could check if it will rain and decide based on that
    # For now, returns "yes" by default
    return {"result": "yes"}

# Main for running with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)