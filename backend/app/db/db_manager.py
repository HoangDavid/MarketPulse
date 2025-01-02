from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticCollection
from decouple import config

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
    
    def get_collection(self, collection_name: str)->AgnosticCollection:
        return self.db[collection_name]
    
    async def find(self, collection: AgnosticCollection, query: dict, limit: int):
        cursor = collection.find(query).limit(limit)
        documents = await  cursor.to_list(length=limit)
        return documents
    
    async def insert_one(self, collection: AgnosticCollection, document):
        result = await collection.insert_one(document)
        return str(result.inserted_id)
    
    async def delete_one(self, collection: AgnosticCollection, query:dict):
        result = await collection.delete_one(query)
        return result.deleted_count
    