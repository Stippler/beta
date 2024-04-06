import asyncio
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
events = client.EventDatabase.EventCollection

async def ping_server():
  # Send a ping to confirm a successful connection
  try:
      await client.admin.command('ping')
      print("Pinged your deployment. You successfully connected to MongoDB!")
  except Exception as e:
      print(e)
      
async def do_insert():
    document = {"template1": "event1"}
    result = await events.insert_one(document)
    print("result %s" % repr(result.inserted_id))
      
# asyncio.run(ping_server())
asyncio.run(do_insert())
# loop = client.get_io_loop()
# loop.run_until_complete(do_insert())