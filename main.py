
# ****************************************************  print messages     ********************************

# from fastapi import FastAPI
# app = FastAPI() # register app


# @app.get("/") # here get is a method  
# def index():
#     return {'message': "hello World"}


# ********************************************* for render template *************************************
from fastapi import FastAPI
from user import router as UserRouter
from tortoise.contrib.fastapi import register_tortoise





app = FastAPI()
app.include_router(UserRouter.router)

register_tortoise(
    app,
    db_url="postgres://postgres:8821@127.0.0.1/crudinfastapi",
    modules={'models': ['user.models',]},
    generate_schemas=True,
    add_exception_handlers=True
)

