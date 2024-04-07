from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, List, Optional 
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta, time
from weather import get_weather_data

import mongo_calls as db

# Load environment variables
# Your key needs to be in the .env file in the root of the project, like this: OPENAI_API_KEY='<your key>'
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
model = "gpt-4-1106-preview"
model_frontend = "gpt-3.5-turbo"

default_task = {
    "title": "Event Title describing the event",
    "date": "yyyy-mm-dd",
    "startTime": "HH:MM",
    "endTime": "HH:MM",
    "activity": "choose best fit from: coffee, drink, eat, meeting, party, running, walking, working, other",
    "description": "Short description of the event or activity.",
    "latitude": "Float describing the Latitude the event will take place",
    "longitude": "Float describing Longitude the event will take place",
    "indoor": "Boolean describing if the event takes place indoor or not."
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
    latitude: float
    longitude: float
    indoor: bool


class IntermidiateTask(BaseModel):
    title: str
    date: str
    startTime: str
    endTime: str
    activity: str
    description: str
    latitude: str
    longitude: str
    indoor: str
    
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
      filled according to the predefined template. This includes fields for title, time, location, and indoor status,
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
    
    template_str = json.dumps(default_task)
    
    task = inter_task_and_text.task
    chat = inter_task_and_text.messages

    completion = None

    if task is None:
        # first try to fill the json
        completion = client.chat.completions.create(
            model=model_frontend,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": f"You are an assistant that extracts information from text. You receive as input a text and you will extract information from it and fill out a template based on it. The values in the json template describe what the keys should store. You return nothing other than the filled-out template in valid json format. Any value that you cannot fill in, you will fill with the word EMPTY as a string. Do not make up information that you cannnot extract from the user input. However, if you can guess the event description or if the event is indoor from its title or description, please fill out these entries. Today is {datetime.now().strftime('%Y-%m-%d')}."},
                {"role": "user", "content": f"{chat[-1]}"},
                {"role": "system", "content": f"The template is: {template_str}"} 
            ]
        )
    else:
        # try to update the json file
        user_answer = chat[-1]
        bot_question = chat[-2]
        completion = client.chat.completions.create(
            model=model_frontend,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": f"You are an assistant that updates a template with new information. You receive as input a question that was asked to the user and its response. Additionally you will get a json template that the user has partially filled out and a json template that describe for each entry what they need to be filled with. You will extract the information from the user response and fill out a template based on it. You return nothing other than the filled-out template in valid json format. The entries not filled by the user are marked with the word EMPTY. Any value that was EMPTY and you cannot fill in, you will leave with the word EMPTY. Do not make up information that you cannnot extract from the user input. If it is possible to guess an event description or if the event is indoor or not, please do so. For longitude and latitude, if a location is given, fill in some estimate for those values. Today is {datetime.now().strftime('%Y-%m-%d')}."},
                {"role": "system", "content": f"The bots question was: {bot_question}"},
                {"role": "system", "content": f"The users answer was: {user_answer}"},
                {"role": "system", "content": f"The initial template describing what each entry should hold is: {template_str}"},
                {"role": "user", "content": f"The template which entries that are EMPTY need to be filled: {task}"} 
            ]
        )
        
    completion_message_content = completion.choices[0].message.content
    task = json.loads(completion_message_content) 
        
    success = True
    
    if "title" not in task:
        task["tite"] = "EMPTY"
    if "date" not in task:
        task["date"] = "EMPTY"
    if "startTime" not in task:
        task["startTime"] = "EMPTY"
    if "endTime" not in task:
        task["endTime"] = "EMPTY"
    if "activity" not in task:
        task["activity"] = "EMPTY"
    if "description" not in task:
        task["description"] = "EMPTY"

    # Iterate over key, value pairs in the first dictionary
    for key, value in task.items():
        # Check if the key is in the second dictionary and has a different value
        if value == "EMPTY":
            success = False
        if key == "taskId":
            continue

    if success:
        check = client.chat.completions.create(
            model=model_frontend,
            messages=[
                {"role": "system", "content": f"You are an assistant that checks if a json was filled out correctly. You receive as input a filled json template and the template which also describes which entry should hold what value. You check if the template was filled correctly. If so, you answer with the number 1. If it was filled out wrong you answer with the number 0. You answer with this number without asking further questions and without giving any reasoning. Types are unimportant, we are only interested in content and format."},
                {"role": "system", "content": f"The initial template describing what each entry should hold is: {template_str}"},
                {"role": "user", "content": f"The template which entries need to be checked is: {task}"} 
            ]
        )
        
        if '0' in check.choices[0].message.content and '1' not in check.choices[0].message.content:
            final_result = {}
            final_result["success"] = False
            final_result["task"] = None
            final_result["message"] = "Unfortunately, something went wrong. Your event was prematurely checked as success by AI. Please try to create the event again."
            return final_result
    
    # analysis
    analysis = None
    if not success:
        analysis = client.chat.completions.create(
            model=model_frontend,
            messages=[
                {"role": "system", "content": f"You are an assistant that asks a user to complete a json template. You receive as input a partially filled json template. The unfilled entries are marked with the word EMPTY or are invalid entries. You search for the first such entry and return a message to politely ask the user to give more information which you would need to fill out this entry. Do not respond with anything other than the request to the user. Only ask for one information from the user at one time! For longitudinal and latitudinal information, ask for the location instead. Ask as simple questions as possible. Do not mention that you are filling out a JSON file."},
                {"role": "user", "content": f"The template is: {task}"} 
            ]
        )
    else:
        analysis = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are an assisstant communication with the user. You  are given a json template describing an event, need to summarize it for the user and tell the user that the event creation was successfull. Only answer with what you have been instructed to. Do not make up something. Be nice to the user."},
                {"role": "user", "content": f"The json is: {task}"} 
            ]
        )
        
    analysis_message_content = analysis.choices[0].message.content
        
    final_result = {}
    
    print(task)

    
    if not success:
        if "latitude" not in task:
            task["latitude"] = "EMPTY"
        if "longitude" not in task:
            task["longitude"] = "EMPTY"
        if "indoor" not in task:
            task["indoor"] = "EMPTY"
    
        task["latitude"] = str(task["latitude"])
        task["longitude"] = str(task["longitude"])
        task["indoor"] = str(task["indoor"])
    
    if success:
        if "latitude" not in task:
            task["latitude"] = 48.42
        if "longitude" not in task:
            task["longitude"] = 21.15
        if "indoor" not in task:
            task["indoor"] = False
            
        try:
            task["latitude"] = float(task["latitude"])
            task["longitude"] = float(task["longitude"])
            task["indoor"] = eval(task["indoor"])
        except:
            task["latitude"] = 48.42
            task["longitude"] = 21.15
            task["indoor"] = False
        
    final_result["task"] = task
    final_result["success"] = success
    final_result["message"] = analysis_message_content
    
    return final_result


@app.post("/propose")
async def propose_new_date(old_text: dict, new_proposed_date: dict):
    """
    Proposes a new date and time for an activity based on the original event details and a proposed time.
    
    This endpoint takes two JSON objects: one containing the original event details, and the other with the proposed
    new date and time. These are passed to the OpenAI API to generate a response suggesting a new time for the activity.
    
    Parameters:
    - old_text (dict): A dictionary object with the original event details, including fields for title, time, location, and indoor status.
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
            model=model,
            response_format={ "type": "json_object" },
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

def convert_to_iso8601(json_dict):
    """
    Convert "date", "startTime", and "endTime" from a JSON dictionary into ISO 8601 format.
    
    :param json_dict: Dictionary containing "date", "startTime", and "endTime" keys.
    :return: Two strings representing the start and end timestamps in ISO 8601 format.
    """
    # Parsing the "date" from "dd/mm/yyyy" to a datetime object
    # date = datetime.strptime(json_dict["date"], "%d/%m/%Y")
    
    # Parsing "startTime" and "endTime" from "hh/mm" to time objects and combining them with "date"
    start_datetime = datetime.strptime(f'{json_dict["date"]} {json_dict["startTime"]}', "%Y-%m-%d %H:%M")
    end_datetime = datetime.strptime(f'{json_dict["date"]} {json_dict["endTime"]}', "%Y-%m-%d %H:%M")

    
    return start_datetime, end_datetime

@app.post("/weather")
async def get_weather(task: Task):
    """
    Input: Task
    Output: Good/Bad
    """
    task = task.model_dump()
    if task["indoor"] is True:
        return {"suitable": "True", "reason": "The event is indoor."}
    from_date, to_date = convert_to_iso8601(task)
    print(from_date, to_date)
    try:
        weather_data = get_weather_data(task["latitude"], task["longitude"], from_date, to_date, task["description"])
    except Exception as e:
        print(e)
        return {"suitable": False, "reason": "Event has already started."}
    try:
        completion = client.chat.completions.create(
            model=model,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are an automated system that checks the weather for an event. Based on the input information for the event and the weather data for this time, you will determine if the weather is suitable for the activity. You will return a response indicating whether the weather is good or bad for the event of the form {suitable: 'True / False', reason: 'reason for decision'}. In your reasoning, explain how the provided parameters impaced your decision making. Make sure to return a valid json object."},
                {"role": "user", "content": f"Task: {task}"}, 
                {"role": "user", "content": f"Weather data: {weather_data}"}
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    print(completion.choices[0].message.content)
    response = json.loads(completion.choices[0].message.content)
    response['suitable'] = response['suitable'] == 'True'
    return response

@app.post("/new_time")
async def propose_new_time(task: Task):
    task_dict = task.model_dump()  # Assuming model_dump converts the Task object into a dictionary
    from_date, to_date = convert_to_iso8601(task_dict)
    alternative_times = []
    now = datetime.now()

    # Time difference constraints
    hours_difference = (from_date - now).total_seconds() / 3600
    future_limit_hours = 96  # 4 days in hours

    # Determine if original time is day or night
    day_start, day_end = time(7, 0), time(19, 0)  # 7:00 to 19:00 considered as day
    original_is_day = day_start <= from_date.time() <= day_end

    # Generate alternative times within the specified constraints
    for i in range(0, future_limit_hours - round(hours_difference), 3):
        if i > 0:  # Ensure time is in the future
            new_date = from_date + timedelta(hours=i)
            new_is_day = day_start <= new_date.time() <= day_end
            if original_is_day == new_is_day:
                alternative_times.append(new_date)
    for i in range(3, round(hours_difference), 3):
        if i > 0:
            new_date = now - timedelta(hours=i)
            new_is_day = day_start <= new_date.time() <= day_end
            if original_is_day == new_is_day:
                alternative_times.append(new_date)
    print(alternative_times)
    # Check weather suitability for each alternative time
    for new_date in alternative_times:
        weather_data = get_weather_data(task_dict["latitude"], task_dict["longitude"], new_date, new_date + timedelta(hours=1), task_dict["description"])
        try:
            completion = client.chat.completions.create(
                model=model,
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": "You are an automated system that checks the weather for an event. Based on the input information for the event and the weather data for this time, you will determine if the weather is suitable for the activity. You will return a response indicating whether the weather is good or bad for the event of the form {suitable: boolean, reason: 'reason for decision'}. In your reasoning, explain how the provided parameters impaced your decision making. Make sure to return a valid json object."},
                    {"role": "user", "content": f"Task: {task}"}, 
                    {"role": "user", "content": f"Weather data: {weather_data}"}
                ]
            )
            response = json.loads(completion.choices[0].message.content) 
            suitable = response["suitable"]
            if suitable == 'True':
                return {"new_time": new_date.strftime("%Y-%m-%d %H:%M:%S"), "answer": suitable == "True"}
        except Exception as e:
            raise HTTPException(status_code=500, detail= "Issue finding new time " + str(e) + "response: " + str(completion.choices[0].message.content))

    return {"new_time": from_date.strftime("%Y-%m-%d %H:%M:%S"), "answer": False}



# Main for running with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)