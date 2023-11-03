# serializer

from pydantic import BaseModel


class Person(BaseModel):
    email:str
    phone:int
    name:str
    password:str


