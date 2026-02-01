from bson import ObjectId
from typing import Optional, Dict, Any

from fastapi import HTTPException


class GroceryRepository:
    def __init__(self, db):
        self.collection = db.groceries

    def create(self, document: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        result = self.collection.insert_one(document)
        return self.collection.find_one({"_id": result.inserted_id})

    def find_by_id(self, id_str: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(id_str)
            return self.collection.find_one({"_id": oid})
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Failed to retrieve created item")
