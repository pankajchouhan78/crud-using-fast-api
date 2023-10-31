
# ****************************************************  print messages     ********************************

# from fastapi import FastAPI
# app = FastAPI() # register app


# @app.get("/") # here get is a method  
# def index():
#     return {'message': "hello World"}


# ********************************************* for render template *************************************
from fastapi import FastAPI
from user import router as UserRouter
# here we import router to handle user related endpoints from user module


app = FastAPI()
app.include_router(UserRouter.router)

# app.include_router(UserRouter.router) ke through UserRouter add kiya hai. Yeh UserRouter module se aane wale endpoints ko include karta hai, jo user related operations ko handle karenge.