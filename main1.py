from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Dict

class SimpleSentimentModel:

    def __init__(self):
        self.positive_words = {"good", "great", "awesome", "love", "excellent", "easy", "fast"}
        self.negative_words = {"bad", "terrible", "slow", "hate", "broken", "difficult", "fail"}

    def predict(self, text: str) -> dict:
        
        words = text.lower().split()
        pos_count = sum(1 for word in words if word in self.positive_words)
        neg_count = sum(1 for word in words if word in self.negative_words)
        
        
        if pos_count > neg_count:
            return {"sentiment": "Positive", "confidence": 0.85}
        elif neg_count > pos_count:
            return {"sentiment": "Negative", "confidence": 0.88}
        else:
            return {"sentiment": "Neutral", "confidence": 0.50}


ml_resources = {}

@asynccontextmanager
async def lifespan(app: FastAPI):

    ml_resources["model"] = SimpleSentimentModel()
    
    yield 
    ml_resources.clear()


app = FastAPI(
    title="Simple CRUD Inference Service",
    lifespan=lifespan
)


IN_MEMORY_DB: Dict[int, dict] = {}
id_counter = 1


class TextData(BaseModel):
    text: str


class InferenceRecord(BaseModel):
    id: int
    text: str
    sentiment: str
    confidence: float


@app.post("/predict", response_model=InferenceRecord, status_code=status.HTTP_201_CREATED)
async def create_prediction(item: TextData):
    global id_counter

    model = ml_resources["model"]
    
    prediction_result = model.predict(item.text)
    
    new_record = {
        "id": id_counter,
        "text": item.text,
        "sentiment": prediction_result["sentiment"],
        "confidence": prediction_result["confidence"]
    }
    
    IN_MEMORY_DB[id_counter] = new_record
    id_counter += 1
    
    return new_record


@app.get("/items", response_model=list[InferenceRecord])
async def read_all_predictions():

    return list(IN_MEMORY_DB.values())



@app.get("/items/{item_id}", response_model=InferenceRecord)
async def read_prediction(item_id: int):
    
    if item_id not in IN_MEMORY_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Inference record with ID {item_id} not found"
        )
    return IN_MEMORY_DB[item_id]


@app.put("/items/{item_id}", response_model=InferenceRecord)
async def update_prediction(item_id: int, updated_item: TextData):
    
    if item_id not in IN_MEMORY_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Cannot update. Record with ID {item_id} not found"
        )
    
    
    model = ml_resources["model"]
    prediction_result = model.predict(updated_item.text)
    
    
    IN_MEMORY_DB[item_id] = {
        "id": item_id,
        "text": updated_item.text,
        "sentiment": prediction_result["sentiment"],
        "confidence": prediction_result["confidence"]
    }
    
    return IN_MEMORY_DB[item_id]


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prediction(item_id: int):
    
    if item_id not in IN_MEMORY_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Cannot delete. Record with ID {item_id} not found"
        )
    
    
    del IN_MEMORY_DB[item_id]
    
    
    return None 