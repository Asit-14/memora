from fastapi import FastAPI, Request
from mockData import products


app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to home of FastAPI!"}

@app.get("/contact")
def contact():
    return {"message": "You can connect with us anytime."}

@app.get("/products")
def get_product():
    return products


# path parameters 

@app.get("/products/{product_id}")
def get_one_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    return {
        "error": "Product not found with this id"
    }


# query parameter

@app.get("/greet")
def greet_user(name: str, age : int):
    return {
        "greet": f"Hello {name}, how are you? i am  {age} old"
    }


# query parameter 

@app.get("/queryparameter")
def user_greet(request: Request):
    query_parameters = dict(request.query_params)
    print(query_parameters)

    return {
        "greet": f"Hello {query_parameters.get('name')} you are {query_parameters.get('age')} years old!"
    }