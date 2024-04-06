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

# Load environment variables
# Your key needs to be in the .env file in the root of the project, like this: OPENAI_API_KEY='<your key>'
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

default_task = {
    "title": "Example Event Title",
    "date": "dd/mm/yyyy",
    "startTime": "HH:MM",
    "endTime": "HH:MM",
    "activity": "choose best fit from: coffee, drink, eat, meeting, party, running, walking, working, other",
    "description": "Short description of the event or activity.",
#   "location": "Example location",
    "latitude": "Float describing the Latitude the event will take place",
    "longitude": "Float describing Longitude the event will take place",
    "sheltered": "Boolean describing if the event takes place in a sheltered place or not"
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
    taskId: Optional[int] = None
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


class IntermidiateTask(BaseModel):
    title: str
    date: str
    startTime: str
    endTime: str
    activity: str
    description: str
#   location: str
    latitude: str
    longitude: str
    sheltered: str
    
class UpdateTextRequest(BaseModel):
    task: Optional[IntermidiateTask] = None
    messages: List[str]

class WeatherRequest(BaseModel):
    longitude: float
    latitude: float
    timeframe: str

class TextRequest(BaseModel):
    text: str

class TextListRequest(BaseModel):
    text: List [str]

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


@app.post("/task/many/", response_description="Add new tasks")
async def create_task(task_list: List [Task]):
    task = await db.add_multiple_tasks([t.model_dump() for t in task_list])
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
    for text in text_request.text.split('\n'):
        line = TextRequest(text=text)
        result = await analyze_text(line)
        results.append(result)
    print(results)
    return results


@app.post("/text")
async def analyze_text(inter_task_and_text: UpdateTextRequest):
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
      
    Return Format:
    {
        sucess: bool
        task: {}
        message: ""
    }
      
    Raises:
    - HTTPException: An error response with status code 500 if there is an issue with the OpenAI API call.
    """
    task = inter_task_and_text.task
    chat = inter_task_and_text.messages

    if(task is None):
        template_str = json.dumps(default_task)
    
        # initial try
        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": f"You are an assistant that extracts information from text. You receive as input a text and you will extract information from it and fill out a template based on it. You return nothing other than the filled-out template in valid json format. Any value that you cannot fill in, you will fill with the word EMPTY. Do not make up information that you cannnot extract from the user input. Today is {datetime.now().strftime('%Y-%m-%d')}."},
                    {"role": "user", "content": f"{chat[0]}"},
                    {"role": "system", "content": f"The template is: {template_str}"} 
                ]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        completion_message_content = completion.choices[0].message.content
        extracted_json = json.loads(completion_message_content)
        
        success = True
        
        result = {}
        # Iterate over key, value pairs in the first dictionary
        for key, value in extracted_json.items():
            # Check if the key is in the second dictionary and has a different value
            if extracted_json[key] == "EMPTY":
                result[key] = "PLEASE FILL OUT!"
                success = False
            else:
                result[key] = value
        
        task = result
    
    # initial try
    #try:
    if len(chat)>1:
        user_message = chat[-2]+chat[-1]
    else:
        user_message = chat[0]
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": f"You are an assistant that updates a template with new information. You receive as input a text and you will extract information from it and fill out a template based on it. You return nothing other than the filled-out template in valid json format. Any value that was not already filled and you cannot fill in, you will fill with the word EMPTY. Do not make up information that you cannnot extract from the user input. Today is {datetime.now().strftime('%Y-%m-%d')}. For longitude and latitude, if a location is given, fill in some estimate for those values. date does have the format 'dd/mm/yyyy'. startTime has the format 'HH:MM'. endTime has the format 'HH:MM'"},
            {"role": "user", "content": f"{user_message}"},
            {"role": "system", "content": f"The template is: {task}"} 
        ]
    )
    #except Exception as e:
    #    raise HTTPException(status_code=500, detail=str(e))
    completion_message_content = completion.choices[0].message.content
    extracted_json = json.loads(completion_message_content)
    
    success = True
    
    result = {}
    # Iterate over key, value pairs in the first dictionary
    for key, value in extracted_json.items():
        # Check if the key is in the second dictionary and has a different value
        if extracted_json[key] == "EMPTY":
            result[key] = "PLEASE FILL OUT!"
            success = False
        else:
            result[key] = value
    
    # analysis
    try:
        analysis = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an assistant that asks a user to complete a json template. You receive as input a not completely filled json template. The unfilled entries are marked with 'PLEASE FILL OUT!'. You search for the first such entry and return a message to politely ask the user to give more information which you would need to fill out this entry. Do not respond with anything other than the request to the user. Only ask for one information from the user at one time! For longitudinal and latitudinal information, ask for the location instead. Ask as simple questions as possible."},
                {"role": "system", "content": f"The template is: {result}"} 
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    analysis_message_content = analysis.choices[0].message.content
    
    final_result = {}
    final_result["success"] = success
    final_result["task"] = result
    final_result["message"] = analysis_message_content
    
    yes_options = {"yes", "y", "true", "t", "1"}
    
    s = final_result["task"]["sheltered"]
    if isinstance(s, str) and s != "PLEASE FILL OUT!":
        if s.strip().lower() in yes_options:
            final_result["task"]["sheltered"] = True
        else:
            final_result["task"]["sheltered"] = False
            
    try:
        final_result["task"]["latitude"] = float(final_result["task"]["latitude"])
    except:
        final_result["task"]["latitude"] = 2.3
        
    try:
        final_result["task"]["longitude"] = float(final_result["task"]["longitude"])
    except:
        final_result["task"]["longitude"] = 2.3
    
    return final_result


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