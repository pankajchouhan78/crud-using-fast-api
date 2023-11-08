from fastapi import APIRouter, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from .models import *
from json import JSONEncoder
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

from .pydentic_modules import Person, DeletePerson, UpdatePerson, LoginPerson,Token

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
    

from passlib.context import CryptContext
from fastapi_login import LoginManager
SECRET = 'your-secret-key'    

manager = LoginManager(SECRET, token_url='/auth/token')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password):
    return pwd_context.hash(password)

@manager.user_loader()  
async def load_user(email: str):
    if await User.exists(email=email):
        user = await User.get(email=email)   
        return user

# Login in users
@app.post('/login/', )
async def login(data: LoginPerson,
                ):
    email = data.email
    user = await load_user(email)
 
    if not user:
        return JSONResponse({'status': False, 'message': 'User not Registered'}, status_code=403)
    elif not verify_password(data.password, user.password):
        return JSONResponse({'status': False, 'message': 'Invalid password'}, status_code=403)
    access_token = manager.create_access_token(
        data={'sub': dict({"id":jsonable_encoder(user.id)}), }
        
    )
    '''test  current user'''
    new_dict = jsonable_encoder(user)
    new_dict.update({"access_token": access_token})
    return Token(access_token=access_token, token_type='bearer')
@app.delete("/delete-person/")
async def delete_person(data:DeletePerson):
    await User.filter(id=data.id).delete()
    return {"User deleted successfully"}

@app.put("/update-person/")
async def update_person(data:UpdatePerson):
    person = await User.get(id=data.id).update(name=data.name, email=data.email, phone=data.phone)
    return person

@app.get('/show-person/')
async def show_person():
    users = await User.all()
    return  users 

@app.delete('/alldelete/')
async def delete_all():
    await User.all().delete()
    return {'All Users Deleted'}