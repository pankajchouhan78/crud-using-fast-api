from fastapi import APIRouter, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from .models import *

from .pydentic_modules import Person

app = APIRouter()



@app.post('/')
async def registration(data:Person):
    phone_number = str(data.phone)
    if len(phone_number) != 10:
        return {"status": "error", "message":"Phone number must be exactly 10 digits"}
    
    if await User.exists(phone = phone_number):
        return {"status": "error", "message":"Phone number already exists"}
    
    elif await User.exists(email = data.email):
        return {"status": "error", "message":"Email already exists"}
    
    else:
        user_object = await User.create(email = data.email, 
                                        name=data.name, 
                                        password=data.password, 
                                        phone=phone_number)
        return user_object



    