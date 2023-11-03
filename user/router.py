from fastapi import APIRouter, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from .models import *


router = APIRouter()
templates = Jinja2Templates(directory="user/templates")

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
        await User.create(name=name, email=email, phone=phone, password=password)
        return RedirectResponse('/table/', status_code = status.HTTP_302_FOUND)
    
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




