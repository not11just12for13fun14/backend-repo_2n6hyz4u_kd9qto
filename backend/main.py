from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Application

app = FastAPI(title="Apex Creative Agency API")

# CORS for local dev + modal host
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ApplicationIn(BaseModel):
    brand_name: str
    website: Optional[str] = None
    instagram: Optional[str] = None
    monthly_revenue: Optional[str] = None
    biggest_struggle: Optional[str] = None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/test")
async def test_db():
    try:
        # Attempt a simple list on a known collection
        _ = db.list_collection_names() if db is not None else []
        return {"database": "ok", "collections": _}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/apply")
async def create_application(payload: ApplicationIn):
    try:
        app_doc = Application(**payload.model_dump())
        inserted_id = create_document("application", app_doc)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/applications")
async def list_applications(limit: int = 20):
    try:
        docs = get_documents("application", limit=limit)
        # Convert ObjectId and datetime to strings for JSON serialization
        def serialize(doc):
            doc["_id"] = str(doc.get("_id")) if doc.get("_id") else None
            for k in ("created_at", "updated_at"):
                if k in doc and doc[k] is not None:
                    doc[k] = str(doc[k])
            return doc
        return [serialize(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
