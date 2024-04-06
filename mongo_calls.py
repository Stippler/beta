import asyncio
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os


def get_client():
    password = os.environ.get("MONGO_DB_KEY")

    if password is None:
        raise Exception("MONDGO_DB_KEY environment variable not set")

    uri_post = "@wheatherornotcluster.3yyvtss.mongodb.net/?retryWrites=true&w=majority&appName=WheatherOrNotCluster"

    uri = "mongodb+srv://" + "jpassweg" + ":" + password + uri_post

    # Set the Stable API version when creating a new client
    client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))
    
    return client


def get_task_collection(username : str):
    client = get_client()
    task_collection = client.TaskDatabase[username]
    return task_collection


async def ping_server():
    # Send a ping to confirm a successful connection
    try:
        client = get_client()
        await client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    

# Database operations
async def add_task(username : str, task_data: dict) -> dict:
    task_collection = get_task_collection(username)
    task = await task_collection.insert_one(task_data)
    print("result %s" % repr(task.inserted_id))
    new_task = await task_collection.find_one({"_id": task.inserted_id})
    return new_task


async def retrieve_tasks(username : str) -> List[dict]:
    task_collection = get_task_collection(username)
    tasks = []
    async for task in task_collection.find():
        tasks.append(task)
    return tasks


async def delete_task(username : str, task : dict) -> bool:
    task_collection = get_task_collection(username)
    coll = task_collection
    n = await coll.count_documents({})
    result = await task_collection.delete_one(task)
    return result.deleted_count > 0
    

async def print_all():
    tasks = await retrieve_tasks()
    for task in tasks:
        print(task)