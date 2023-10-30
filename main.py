from fastapi import FastAPI

app = FastAPI() # register app


@app.get("/") # here get is a method  
def index():
    return {'message': "hello World"}