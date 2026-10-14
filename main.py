from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from enum import Enum

app = FastAPI()

products = []

class Category(str, Enum):
    terminal = "terminal"
    router = "router"

class Brand(str, Enum):
    hikvision = "Hikvision"
    dahua = "Dahua"

class Product(BaseModel):
    id: int
    name: str
    brand: Brand
    description: str
    category: Category

class ProductShort(BaseModel):
    id: int
    name: str
    category: Category

class ProductUpdate(BaseModel):
    id: int | None = None
    name: str | None = None
    brand: Brand | None = None
    description: str | None = None
    category: Category | None = None

def find_index(product_id: int) -> int:
    for i, product in enumerate(products):
        if product.id == product_id:
            return i
    raise HTTPException(status_code=404, detail="Продукт не найден")

def check_id(product_id: int):
    for product in products:
        if product.id == product_id:
            raise HTTPException(status_code=400, detail="Продукт с таким id уже существует")

def apply_update(index: int, data: dict):
    if "id" in data and data["id"] != products[index].id:
        check_id(data["id"])
    products[index] = products[index].model_copy(update=data)
    return products[index]


@app.get("/products", response_model=list[ProductShort])
def get_products(category: Category | None = None):
    if category:
        return [product for product in products if product.category == category]
    return products

@app.get("/products/{product_id}")
def get_product(product_id: int):
    index = find_index(product_id)
    return products[index]

@app.post("/products")
def add_product(product: Product):
    check_id(product.id)
    products.append(product)
    return product

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    index = find_index(product_id)
    product = products.pop(index)
    return product

@app.patch("/products/{product_id}")
def update_product(product_id: int, product: ProductUpdate):
    index = find_index(product_id)
    return apply_update(index, product.model_dump(exclude_unset=True))