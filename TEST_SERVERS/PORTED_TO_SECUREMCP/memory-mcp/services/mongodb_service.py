from typing import Dict, List, Optional
import pymongo
import pymongo.synchronous
from src.core.logger import logger
from pymongo.errors import ConnectionFailure, OperationFailure

class MongoDBService:
    def __init__(self, connection_string: str, database_name: str):
        """Initialize the MongoDB service."""
        try:
            self.client = pymongo.MongoClient(connection_string)
            # Ping the server to verify connection
            self.client.admin.command("ping")
            self.db = self.client[database_name]
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def get_client(self) -> pymongo.MongoClient:
        """Get the MongoDB client."""
        return self.client
    
    def get_database(self) -> pymongo.synchronous.database.Database:
        """Get the MongoDB database."""
        return self.db
    
    def get_collection(self, collection_name: str) -> pymongo.synchronous.collection.Collection:
        """Get a collection from the database."""
        try:
            return self.db[collection_name]
        except Exception as e:
            logger.error(f"Error accessing collection {collection_name}: {str(e)}")
            raise
    
    def aggregate(self, collection_name: str, pipeline: List[Dict]) -> List[Dict]:
        """Perform an aggregation operation on a collection."""
        try: 
            result = self.db[collection_name].aggregate(pipeline)
            return list(result)
        except Exception as e:
            logger.error(f"Error performing aggregation: {str(e)}")
            raise

def get_mongodb_service(connection_string: str, database_name: str) -> MongoDBService:
    """Get a MongoDB service instance."""
    return MongoDBService(connection_string, database_name)
