from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

app = FastAPI()

products = []

class Todo(BaseModel):
    title: str

def check_index(index: int):
    if index < 0 or index >= len(todos):
        raise HTTPException(status_code=404, detail="Задача не найдена")

@app.get("/todos")
def get_todos():
    return todos
@app.post("/todos")

def add_todo(todo: Todo):
    todos.append(todo)
    return todo

@app.delete("/products/{index}")
def delete_product(index: int):
    check_index(index)
    product = products.pop(index)
    return product

@app.put("/todos/{index}")
def update_todo(index: int, todo: Todo):
    check_index(index)
    todos[index] = todo
    return todo