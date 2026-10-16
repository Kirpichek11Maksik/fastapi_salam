from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from enum import Enum


app = FastAPI()

terminals_storage = []
routers_storage = []
brackets_storage = []


class TerminalBrands(str, Enum):
    HikVision = "HikVision"
    Dahua = "Dahua"

class Location(BaseModel):
    region: str
    district: str
    city: str
    street: str

class Capacity(BaseModel):
    capacity_human: int
    capacity_card: int
    user_registered: int

class Terminal(BaseModel):
    id_number: int
    brand: TerminalBrands
    ser_num: int
    version_po: int
    capacity: Capacity
    location: Location
    router_id: int | None = None

class Router(BaseModel):
    id_number: int
    ip: str
    location: Location

class Bracket(BaseModel):
    id_number: int
    location: Location


def check_id(id_num: int, storage: list):
    if id_num in [item.id_number for item in storage]:
        raise HTTPException(status_code=400, detail="Устройство с таким id уже существует")

def find_by_id(id_num: int, storage: list):
    for item in storage:
        if item.id_number == id_num:
            return item
    return None

def search_by_location(location: str, storage: list):
    result = []
    for i in storage:
        fields = [i.location.region, i.location.district, i.location.city, i.location.street]
        if any(location.lower() in f.lower() for f in fields):
            result.append(i)
    if len(result) == 0:
        raise HTTPException(status_code=404, detail="Ничего не найдено по такому местоположению")
    return result


@app.get("/terminals")
def get_terminals(location: str | None = None):
    if location is None:
        return terminals_storage
    return search_by_location(location, terminals_storage)

@app.post("/terminals")
def create_terminal(terminal: Terminal):
    check_id(terminal.id_number, terminals_storage)

    if terminal.router_id is not None:
        router = find_by_id(terminal.router_id, routers_storage)
        if router is None:
            raise HTTPException(status_code=404, detail="Маршрутизатор с таким id не найден")
        if terminal.location != router.location:
            raise HTTPException(status_code=400, detail="Локация терминала должна совпадать с локацией маршрутизатора")

    terminals_storage.append(terminal)
    return terminal

@app.delete("/terminals/{id_number}")
def delete_terminal(id_number: int):
    for terminal in terminals_storage:
        if terminal.id_number == id_number:
            terminals_storage.remove(terminal)
            return {"message": "Терминал успешно удален"}
    raise HTTPException(status_code=404, detail="Терминал с таким id не найден")


@app.get("/routers")
def get_routers(location: str | None = None):
    if location is None:
        return routers_storage
    return search_by_location(location, routers_storage)

@app.post("/routers")
def create_router(router: Router):
    check_id(router.id_number, routers_storage)
    routers_storage.append(router)
    return router

@app.get("/routers/{id_number}/terminals")
def get_router_terminals(id_number: int):
    router = find_by_id(id_number, routers_storage)
    if router is None:
        raise HTTPException(status_code=404, detail="Маршрутизатор с таким id не найден")
    return [t for t in terminals_storage if t.router_id == id_number]


@app.get("/brackets")
def get_brackets(location: str | None = None):
    if location is None:
        return brackets_storage
    return search_by_location(location, brackets_storage)

@app.post("/brackets")
def create_bracket(bracket: Bracket):
    check_id(bracket.id_number, brackets_storage)
    brackets_storage.append(bracket)
    return bracket