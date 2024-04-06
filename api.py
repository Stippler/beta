from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, List, Optional 
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime


# Load environment variables
# Your key needs to be in the .env file in the root of the project, like this: OPENAI_API_KEY='<your key>'
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

template = {
  "title": "Example Event Title",
  "activity": "1-word activity type",
  "date": "dd/mm/yyyy",
  "from": "HH:MM",
  "to": "HH:MM",
  "description": "Short description of the event or activity.",
  "city": "Example City",
  "location_gps": "Latitude, Longitude",
  "sheltered": "Boolean",
}

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
    """
    Analyzes the input text and extracts information to fill out a predefined template.
    
    This endpoint takes a JSON object containing a "text" field, which is passed to the OpenAI API. The response
    from OpenAI, structured according to the specified template, is then returned as a JSON object.
    
    Parameters:
    - text_request (TextRequest): A request model containing the "text" field with the input sentence or paragraph.
    
    Returns:
    - dict: A dictionary object with a single key "result". The value is a JSON object extracted from the OpenAI API response,
      filled according to the predefined template. This includes fields for title, time, location, and sheltered status,
      structured based on the input text's analysis.
      
    Raises:
    - HTTPException: An error response with status code 500 if there is an issue with the OpenAI API call.
    """
    template_str = json.dumps(template)
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": f"You are an assistant that extracts information from text. You receive as input a text and you will extract information from it and fill out a template based on it. You return nothing other than the filled-out template in valid json format. Today is {datetime.now().strftime('%Y-%m-%d')}."},
                {"role": "user", "content": text_request.text},
                {"role": "system", "content": f"The template is: {template_str}"}
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    completion_message_content = completion.choices[0].message.content
    extracted_json = json.loads(completion_message_content)
    return {"result": extracted_json}

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