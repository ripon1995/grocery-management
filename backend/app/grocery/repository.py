from typing import Optional, Dict, Any

from bson import ObjectId
from fastapi import HTTPException

from backend.app.grocery.models import Grocery


class GroceryRepository:
    def __init__(self, db):
        self.collection = db.groceries

    def create(self, grocery: Grocery) -> Dict[str, Any]:
        document = grocery.model_dump(mode='json')
        result = self.collection.insert_one(document)
        return self.collection.find_one({"_id": result.inserted_id})

    def find_by_id(self, id_str: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(id_str)
            return self.collection.find_one({"_id": oid})
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Failed to retrieve created item")

    def update(self, id_str: str, update_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update document with $set operation and return the new version
        """
        try:
            oid = ObjectId(id_str)
            updated = self.collection.find_one_and_update(
                {"_id": oid},
                {"$set": update_fields},
                return_document=True
            )
            return updated
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

    def find_all(self) -> list[Dict[str, Any]]:
        try:
            result = self.collection.find().limit(100)
            return list(result)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Failed to retrieve items")
