from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, List, Optional 
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime

import mongo_calls as db

unique_id = 5

# Load environment variables
# Your key needs to be in the .env file in the root of the project, like this: OPENAI_API_KEY='<your key>'
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

default_task = {
    "taskId": "unique_id",
    "title": "Example Event Title",
    "date": "dd/mm/yyyy",
    "startTime": "HH:MM",
    "endTime": "HH:MM",
    "activity": "choose best fit from: coffee, drink, eat, meeting, party, running, walking, working, other",
    "description": "Short description of the event or activity.",
#   "location": "Example location",
    "latitude": "Latitude",
    "longitude": "Longitude",
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
    taskID: int
    title: str
    date: str
    startTime: str
    endTime: str
    activity: str
    description: str
#   location: str
    latitude: float
    longitude: float
    sheltered: bool

class WeatherRequest(BaseModel):
    longitude: float
    latitude: float
    timeframe: str

class TextRequest(BaseModel):
    text: str

class TextListRequest(BaseModel):
    texts: List[str]

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# Endpoints
@app.post("/task/", response_description="Add new task", response_model=Task)
async def create_task(task: Task):
    task = await db.add_task(task.model_dump())
    if task is not None:
        return task
    raise HTTPException(status_code=500, detail="Task could not be created")


@app.get("/task", response_description="List all tasks", response_model=List[Task])
async def list_tasks():
    tasks = await db.retrieve_tasks()
    if tasks is not None:
        return tasks
    raise HTTPException(status_code=500, detail="Error retrieving tasks list")


@app.put("/task", response_description="Update a task")
async def update_task(new_task: Task):
    task = await db.update_task(new_task.model_dump())
    if task is not None:
        return task
    raise HTTPException(status_code=500, detail="Task could not be replaced")


@app.put("/task/{id}", response_description="Delete a task")
async def delete_task(id : int):
    deleted_task = await db.delete_task(id)
    if deleted_task is not None:
        return deleted_task
    raise HTTPException(status_code=500, detail="Task could not be deleted")


@app.post("/text_list")
async def analyze_text_list(text_request: TextListRequest):
    results = []
    for text in text_request.texts:
        line = TextRequest(text=text)
        result = await analyze_text(line)
        results.append(result)
    return {results}


@app.post("/text")
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
    template_str = json.dumps(default_task)
    global unique_id
    unique_id += 1
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": f"You are an assistant that extracts information from text. You receive as input a text and you will extract information from it and fill out a template based on it. You return nothing other than the filled-out template in valid json format. Any value that you cannot fill in, you will keep the example value of the template. Do not make up information that you cannnot extract from the user input. Today is {datetime.now().strftime('%Y-%m-%d')} and use the taskId {unique_id}."},
                {"role": "user", "content": f"{text_request.text}"},
                {"role": "system", "content": f"The template is: {template_str}"} 
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    completion_message_content = completion.choices[0].message.content
    extracted_json = json.loads(completion_message_content)
    return {"result": extracted_json}


@app.post("/propose")
async def propose_new_date(old_text: dict, new_proposed_date: dict):
    """
    Proposes a new date and time for an activity based on the original event details and a proposed time.
    
    This endpoint takes two JSON objects: one containing the original event details, and the other with the proposed
    new date and time. These are passed to the OpenAI API to generate a response suggesting a new time for the activity.
    
    Parameters:
    - old_text (dict): A dictionary object with the original event details, including fields for title, time, location, and sheltered status.
    - new_proposed_date (dict): A dictionary object with the proposed new date and time for the activity.
    
    Returns:
    - dict: A dictionary object with a single key "result". The value is a string containing the response generated by the OpenAI API,
      suggesting a new time for the activity based on the input information.
      
    Raises:
    - HTTPException: An error response with status code 500 if there is an issue with the OpenAI API call.
    """
    old_str = json.dumps(old_text)
    new_str = json.dumps(new_proposed_date)
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an automated system that formulates a rescheduling because the weather is bad during the original activity plan. Based on input information for an event and a new proposed time, you will write a short text where you propose the new time for the activity. An example might be: 'Due to rain during this time, you might want to reschedule your meeting for tomorrow'. Today is {datetime.now().strftime('%Y-%m-%d')}."},
                {"role": "user", "content": f"Activity: {old_str}"},
                {"role": "user", "content": f"Propose the following time: {new_str}"}
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    completion_message_content = completion.choices[0].message.content
    return {"result": completion_message_content}


@app.post("/weather")
async def get_weather(weather_request: WeatherRequest):
    # Placeholder for fetching weather data based on location and timeframe
    # You should replace this with a call to a real weather API
    # For demonstration, it returns an empty list
    return {}


@app.post("/ok")
async def check_weather_ok(weather_request: WeatherRequest):
    # Placeholder for logic to determine if weather is OK for an event
    # This could check if it will rain and decide based on that
    # For now, returns "yes" by default
    return {"result": "yes"}


# Main for running with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)