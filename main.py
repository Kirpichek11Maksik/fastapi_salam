from datetime import date
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

app = FastAPI()

class RefIn(BaseModel):
    name: str

class Ref(BaseModel):
    id: int
    name: str

class LocationIn(BaseModel):
    name: str
    address: str | None = None

class Location(LocationIn):
    id: int

class DeliveryIn(BaseModel):
    supplier: str
    delivery_date: date
    doc_number: str | None = None

class Delivery(DeliveryIn):
    id: int

class TerminalDetails(BaseModel):
    version_po: int
    capacity_human: int
    capacity_card: int
    user_registered: int

class DeviceIn(BaseModel):
    type_id: int
    manufacturer_id: int
    ser_num: str
    delivery_id: int
    status_id: int | None = None
    location_id: int | None = None
    router_id: int | None = None
    ip: str | None = None
    terminal_details: TerminalDetails | None = None

class Device(DeviceIn):
    id: int

device_types = [Ref(id=1, name="terminal"), Ref(id=2, name="router"), Ref(id=3, name="bracket")]
manufacturers = [Ref(id=1, name="HikVision"), Ref(id=2, name="Dahua"), Ref(id=3, name="MikroTik")]
statuses = [Ref(id=1, name="not_installed"), Ref(id=2, name="online"), Ref(id=3, name="offline")]
locations = []
deliveries = []
devices = []

def next_id(storage: list):
    return max((item.id for item in storage), default=0) + 1

def get_or_404(id_num: int, storage: list, what: str):
    for item in storage:
        if item.id == id_num:
            return item
    raise HTTPException(status_code=404, detail=f"{what} с таким id не найден")

def add_ref_routes(path: str, storage: list):
    @app.get(f"/{path}")
    def get_all():
        return storage

    @app.post(f"/{path}")
    def create(data: RefIn):
        if any(i.name.lower() == data.name.lower() for i in storage):
            raise HTTPException(status_code=400, detail="Такое значение уже есть")
        item = Ref(id=next_id(storage), name=data.name)
        storage.append(item)
        return item

add_ref_routes("device-types", device_types)
add_ref_routes("manufacturers", manufacturers)
add_ref_routes("statuses", statuses)

@app.get("/locations")
def get_locations():
    return locations

@app.post("/locations")
def create_location(data: LocationIn):
    location = Location(id=next_id(locations), **data.model_dump())
    locations.append(location)
    return location

@app.get("/deliveries")
def get_deliveries():
    return deliveries

@app.post("/deliveries")
def create_delivery(data: DeliveryIn):
    delivery = Delivery(id=next_id(deliveries), **data.model_dump())
    deliveries.append(delivery)
    return delivery

@app.post("/devices")
def create_device(data: DeviceIn):
    dtype = get_or_404(data.type_id, device_types, "Тип устройства")
    get_or_404(data.manufacturer_id, manufacturers, "Производитель")
    get_or_404(data.delivery_id, deliveries, "Доставка")
    if data.status_id is not None:
        get_or_404(data.status_id, statuses, "Статус")
    if data.location_id is not None:
        get_or_404(data.location_id, locations, "Локация")

    if any(d.ser_num == data.ser_num for d in devices):
        raise HTTPException(status_code=400, detail="Серийный номер уже занят")

    if dtype.name == "terminal" and data.terminal_details is None:
        raise HTTPException(status_code=400, detail="Заполните параметры устройства")
    if dtype.name != "terminal" and data.terminal_details is not None:
        raise HTTPException(status_code=400, detail="Эти параметры здесь не нужны")

    if data.router_id is not None:
        router = get_or_404(data.router_id, devices, "Маршрутизатор")
        if get_or_404(router.type_id, device_types, "Тип устройства").name != "router":
            raise HTTPException(status_code=400, detail="Указанное устройство не роутер")
        if data.location_id != router.location_id:
            raise HTTPException(status_code=400, detail="Локация не совпадает с роутером")

    if data.ip is not None:
        if any(d.ip == data.ip and d.router_id == data.router_id for d in devices):
            raise HTTPException(status_code=400, detail="IP уже занят в этой сети")

    device = Device(id=next_id(devices), **data.model_dump())
    devices.append(device)
    return device

@app.get("/devices")
def get_devices(
    location: str | None = None,
    type_id: int | None = None,
    manufacturer_id: int | None = None,
    status_id: int | None = None,
    router_id: int | None = None,
):
    result = devices

    if location is not None:
        text = location.lower()
        ids = [
            loc.id for loc in locations
            if text in loc.name.lower() or (loc.address and text in loc.address.lower())
        ]
        result = [d for d in result if d.location_id in ids]
    if type_id is not None:
        result = [d for d in result if d.type_id == type_id]
    if manufacturer_id is not None:
        result = [d for d in result if d.manufacturer_id == manufacturer_id]
    if status_id is not None:
        result = [d for d in result if d.status_id == status_id]
    if router_id is not None:
        result = [d for d in result if d.router_id == router_id]

    return result

@app.get("/devices/{device_id}")
def get_device(device_id: int):
    return get_or_404(device_id, devices, "Устройство")

@app.delete("/devices/{device_id}")
def delete_device(device_id: int):
    device = get_or_404(device_id, devices, "Устройство")
    if any(d.router_id == device_id for d in devices):
        raise HTTPException(status_code=400, detail="К этому устройству подключены другие, сначала удалите их")
    devices.remove(device)
    return {"message": "Устройство успешно удалено"}