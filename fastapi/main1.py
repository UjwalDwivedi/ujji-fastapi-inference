from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Dict
import logging
import sys
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True
)

for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    logging.getLogger(logger_name).handlers.clear()
    logging.getLogger(logger_name).propagate = True

logger = logging.getLogger("inference_service")

class SimpleSentimentModel:
    def __init__(self):
        self.positive_words = {"good", "great", "awesome", "love", "excellent", "easy", "fast"}
        self.negative_words = {"bad", "terrible", "slow", "hate", "broken", "difficult", "fail"}

    def predict(self, text: str) -> dict:
        words = text.lower().split()
        pos_count = sum(1 for word in words if word in self.positive_words)
        neg_count = sum(1 for word in words if word in self.negative_words)
        
        if pos_count == 0 and neg_count == 0:
            logger.warning(f"No recognized sentiment words found in text: '{text}'")
        
        if pos_count > neg_count:
            return {"sentiment": "Positive", "confidence": 0.85}
        elif neg_count > pos_count:
            return {"sentiment": "Negative", "confidence": 0.88}
        else:
            return {"sentiment": "Neutral", "confidence": 0.50}

ml_resources = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Inference Service and loading ML resources...")
    ml_resources["model"] = SimpleSentimentModel()
    yield 
    logger.info("Shutting down Inference Service and clearing ML resources...")
    ml_resources.clear()

app = FastAPI(title="Simple CRUD Inference Service", lifespan=lifespan)

Instrumentator().instrument(app).expose(app)

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
    logger.info(f"POST /predict - Received prediction request for text: '{item.text}'")
    if len(item.text.strip()) < 3:
        logger.warning(f"Very short text received for prediction: '{item.text}'")
    model = ml_resources["model"]
    prediction_result = model.predict(item.text)
    new_record = {
        "id": id_counter,
        "text": item.text,
        "sentiment": prediction_result["sentiment"],
        "confidence": prediction_result["confidence"]
    }
    IN_MEMORY_DB[id_counter] = new_record
    logger.info(f"Created prediction ID {id_counter} with sentiment: {prediction_result['sentiment']}")
    id_counter += 1
    return new_record

@app.get("/items", response_model=list[InferenceRecord])
async def read_all_predictions():
    logger.info("GET /items - Fetching all records")
    return list(IN_MEMORY_DB.values())

@app.get("/items/{item_id}", response_model=InferenceRecord)
async def read_prediction(item_id: int):
    logger.info(f"GET /items/{item_id} - Fetching record")
    if item_id < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Item ID cannot be negative.")
    if item_id not in IN_MEMORY_DB:
        logger.error(f"GET /items/{item_id} FAILED - Record not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inference record with ID {item_id} not found")
    return IN_MEMORY_DB[item_id]

@app.put("/items/{item_id}", response_model=InferenceRecord)
async def update_prediction(item_id: int, updated_item: TextData):
    logger.info(f"PUT /items/{item_id} - Updating record")
    if item_id<0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Item ID cannot be negative.")
    if item_id not in IN_MEMORY_DB:
        logger.error(f"PUT /items/{item_id} FAILED - Record not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot update. Record with ID {item_id} not found")
    model = ml_resources["model"]
    prediction_result = model.predict(updated_item.text)
    IN_MEMORY_DB[item_id] = {
        "id": item_id,
        "text": updated_item.text,
        "sentiment": prediction_result["sentiment"],
        "confidence": prediction_result["confidence"]
    }
    logger.info(f"Successfully updated record ID {item_id}")
    return IN_MEMORY_DB[item_id]

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prediction(item_id: int):
    logger.info(f"DELETE /items/{item_id} - Attempting deletion")
    
    if item_id < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Item ID cannot be negative.")
    if item_id not in IN_MEMORY_DB:
        logger.error(f"DELETE /items/{item_id} FAILED - Record not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot delete. Record with ID {item_id} not found")
    del IN_MEMORY_DB[item_id]
    logger.info(f"Successfully deleted record ID {item_id}")
    return None