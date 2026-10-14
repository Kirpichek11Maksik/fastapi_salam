from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

app = FastAPI()

products = []

class Product(BaseModel):
    id: int
    name: str
    description: str
    category: str

def check_index(index: int):
    if index < 0 or index >= len(products):
        raise HTTPException(status_code=404, detail="Продукт не найден")

class ProductShort(BaseModel):
    id: int
    name: str
    category: str

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
    products.append(product)
    return product

@app.delete("/products/{index}")
def delete_product(index: int):
    check_index(index)
    product = products.pop(index)
    return product

@app.put("/products/{index}")
def update_product(index: int, product: Product):
    check_index(index)
    products[index] = product
    return product