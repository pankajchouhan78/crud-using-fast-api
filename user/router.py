from fastapi import APIRouter, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from .models import *
from passlib.context import CryptContext

from fastapi_login import LoginManager
SECRET = 'your-secret-key'


router = APIRouter()
templates = Jinja2Templates(directory="user/templates")
manager = LoginManager(SECRET, token_url='/auth/token')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password):
    return pwd_context.hash(password)


@router.get('/', response_class = HTMLResponse )
async def read_item(request:Request):
    return templates.TemplateResponse('index.html', {'request': request})

@router.post('/registration/', response_class= HTMLResponse)
async def registration(request:Request,
                    name: str = Form(...),
                    email:str = Form(...),
                    password:str = Form(...),
                    phone:str = Form(...)):
    if await User.filter(email=email).exists():
        raise HTMLResponse(status_code=409, detail='User already exists')
    
    elif await User.filter(phone=phone).exists():
        raise HTMLResponse(status_code=409, detail='Phone number already exists')
    else:
        await User.create(name=name, email=email, phone=phone, password=get_password_hash(password))
        return RedirectResponse('/table/', status_code = status.HTTP_302_FOUND)
    

@router.get('/loginshow/',response_class=HTMLResponse)
async def login_show(request:Request):
    return templates.TemplateResponse('login.html', {'request': request})

@manager.user_loader()
async def load_user(phone: str):
    if await User.exists(phone=phone):
        user = await User.get(phone=phone)
        return user


@router.post('/loginuser/')
async def login(request: Request, 
                Phone: str = Form(...),
                Password: str = Form(...)):
    Phone = Phone
    user = await load_user(Phone)
    if not user:
        return {'USER NOT REGISTERED'}
    elif not verify_password(Password, user.password):
        return {'PASSWORD IS WRONG'}
    access_token = manager.create_access_token(
        data=dict(sub=Phone)
    )
    print(access_token)
    # if "_messages" not in request.session:
    #     request.session['_messages'] = []
    #     new_dict = {"user_id": str(
    #         user.id), "Phone": Phone, "access_token": str(access_token)}
    #     request.session['_messages'].append(
    #         new_dict
    #     )
    return RedirectResponse('/table/', status_code=status.HTTP_302_FOUND)

@router.get('/table/', response_class = HTMLResponse )
async def table(request:Request):
    users = await User.all()
    return templates.TemplateResponse('table.html', {'request': request, 'users':users})

@router.get('/deleteuser/{id}', response_class=HTMLResponse)
async def deleteUser(request:Request, id:int):
    await User.get(id=id).delete()
    return RedirectResponse('/table/',status_code = status.HTTP_302_FOUND)

@router.get('/updateuser/{id}', response_class=HTMLResponse)
async def updateuser(request:Request, id=id):
    user = await User.get(id=id)
    return templates.TemplateResponse('updateuser.html', {'request': request, 'user':user})

@router.post('/updateuser/{id}', response_class=HTMLResponse)
async def updateuser(request:Request, id=int,
                     name: str = Form(...),
                     email: str = Form(...),
                     phone: str = Form(...)):
    user = await User.get(id=id)
    if user:
        user.name = name
        user.email = email
        user.phone = phone
        await user.save()
        print("user save")
        return RedirectResponse('/table/', status_code=status.HTTP_302_FOUND) 
    print("user not found")
    return HTMLResponse(status_code=409, detail='User not found')




