import asyncio
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os

username = "jpassweg"
password = os.environ.get("MONGO_DB_KEY")

if password is None:
    raise Exception("MONDGO_DB_KEY environment variable not set")

uri_post = "@wheatherornotcluster.3yyvtss.mongodb.net/?retryWrites=true&w=majority&appName=WheatherOrNotCluster"

uri = "mongodb+srv://" + username + ":" + password + uri_post

# Set the Stable API version when creating a new client
client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))
task_collection = client.TaskDatabase[username]

async def ping_server():
  # Send a ping to confirm a successful connection
  try:
      await client.admin.command('ping')
      print("Pinged your deployment. You successfully connected to MongoDB!")
  except Exception as e:
      print(e)
    
# Database operations
async def add_task(task_data: dict) -> dict:
    task = await task_collection.insert_one(task_data)
    print("result %s" % repr(task.inserted_id))
    new_task = await task_collection.find_one({"_id": task.inserted_id})
    return new_task

async def retrieve_tasks() -> List[dict]:
    tasks = []
    async for task in task_collection.find():
        tasks.append(task)
    return tasks

async def delete_task(document : dict) -> bool:
    coll = task_collection
    n = await coll.count_documents({})
    result = await task_collection.delete_one(document)
    return result.deleted_count > 0

async def print_all():
    tasks = await retrieve_tasks()
    for task in tasks:
        print(task)

loop = asyncio.get_event_loop()     
document = {"template1": "event1"}      
 
loop.run_until_complete(add_task(document))
loop.run_until_complete(delete_task(document))
loop.run_until_complete(print_all())