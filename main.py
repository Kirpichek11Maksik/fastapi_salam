from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

app = FastAPI()

products = []

class Product(BaseModel):
    id: int
    name: str
    description: str
    category: str

class ProductShort(BaseModel):
    id: int
    name: str
    category: str

class ProductUpdate(BaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    category: str | None = None

def check_index(index: int):
    if index < 0 or index >= len(products):
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
def get_products(category: str | None = None):
    if category:
        return [product for product in products if product.category.lower() == category.lower()]
    return products

@app.get("/products/{index}")
def get_product(index: int):
    check_index(index)
    return products[index]

@app.post("/products")
def add_product(product: Product):
    check_id(product.id)
    products.append(product)
    return product

@app.delete("/products/{index}")
def delete_product(index: int):
    check_index(index)
    product = products.pop(index)
    return product

@app.patch("/products/{index}")
def update_product(index: int, product: ProductUpdate):
    check_index(index)
    return apply_update(index, product.dict(exclude_unset=True))