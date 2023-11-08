# serializer

from pydantic import BaseModel


class Person(BaseModel):
    email:str
    phone:int
    name:str
    password:str

class DeletePerson(BaseModel):
    id: int

class UpdatePerson(BaseModel):
    id: int
    name:str
    email:str
    phone:int

class LoginPerson(BaseModel):
    email:str
    password:str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"