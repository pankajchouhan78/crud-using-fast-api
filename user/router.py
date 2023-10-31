from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="user/templates")

@router.get('/', response_class = HTMLResponse )
async def read_item(request:Request):
    return templates.TemplateResponse('index.html', {'request': request})

