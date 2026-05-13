# test_cosmos.py
import asyncio
from azure.cosmos.aio import CosmosClient

COSMOS_ENDPOINT = "YOUR_COSMOS_ENDPOINT_HERE"
COSMOS_KEY = "YOUR_COSMOS_KEY_HERE"
DATABASE = "YOUR_DATABASE_NAME_HERE"
CONTAINER = "YOUR_CONTAINER_NAME_HERE"

async def test_write():
    async with CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY) as client:
        db = client.get_database_client(DATABASE)
        container = db.get_container_client(CONTAINER)
        
        doc = {
            "id": "test-001",
            "event_id": "test-001",
            "symbol": "JSE:SOL",
            "price": 23550,
            "asset_class": "EQUITY"
        }
        
        result = await container.create_item(doc)
        print(f"Document written successfully: {result['id']}")

asyncio.run(test_write())