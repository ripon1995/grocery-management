from typing import Optional, Dict, Any, List

from bson import ObjectId
from fastapi import HTTPException

from backend.app.grocery.models import Grocery


class GroceryRepository:
    def __init__(self, db):
        self.collection = db.groceries

    def create(self, grocery: Grocery) -> Grocery:
        document = grocery.model_dump(mode='json')
        result = self.collection.insert_one(document)
        saved_doc = self.collection.find_one({"_id": result.inserted_id})
        saved_doc["_id"] = str(saved_doc["_id"])
        return Grocery(**saved_doc)

    def find_by_id(self, id_str: str) -> Optional[Grocery]:
        try:
            oid = ObjectId(id_str)
            doc = self.collection.find_one({"_id": oid})
            if not doc:
                return None
            doc["_id"] = str(doc["_id"])
            return Grocery(**doc)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Failed to retrieve created item")

    def update(self, id_str: str, update_fields: Dict[str, Any]) -> Optional[Grocery]:
        """
        Update document with $set operation and return the new version
        """
        try:
            oid = ObjectId(id_str)
            updated_doc = self.collection.find_one_and_update(
                {"_id": oid},
                {"$set": update_fields},
                return_document=True
            )
            if not updated_doc:
                return None
            updated_doc["_id"] = str(updated_doc["_id"])
            return Grocery(**updated_doc)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

    def find_all(self) -> List[Grocery]:
        try:
            # 1. Fetch from MongoDB
            cursor = self.collection.find().limit(100)

            results = []
            for doc in cursor:
                # 2. Convert _id (ObjectId) to id (string) for each document
                doc["_id"] = str(doc["_id"])

                # 3. Use the Grocery model to validate and structure the data
                results.append(Grocery(**doc))

            return results
        except Exception as e:
            # Log the actual error for debugging
            print(f"Error in find_all: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve items")
