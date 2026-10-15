from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from enum import Enum


app = FastAPI()

storage = []

class Brands(str, Enum):
    HikVision = "HikVision"
    Dahua = "Dahua"

class Location(BaseModel):
    region: str
    district: str
    city: str
    street: str

class Terminal(BaseModel):
    brand: Brands
    id_number: int
    ser_num: int
    version_po: int
    capacity: int
    location: Location

@app.post("/terminals")
def create_terminal(terminal: Terminal):
    storage.append(terminal)
    return storage

@app.get("/terminals/{id_number}")
def get_terminal(id_number: int):

    for i in storage:
        if id_number == i.id_number:
            return i

    raise HTTPException(
        status_code=404,
        detail="Терминал с таким id не найден"
    )

@app.delete("/terminals/{id_number}")
def delete_terminal(id_number: int):
    for terminal in storage:
        if terminal.id_number == id_number:
            storage.remove(terminal)
            return {"message": "Терминал успешно удален"}
    raise HTTPException(
        status_code=404,
        detail="Терминал с таким id не найден"
    )