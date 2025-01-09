from fastapi import FastAPI
from sqladmin import Admin, ModelView
from models import engine, Parent, Child

app = FastAPI()
admin = Admin(app, engine)


class ParentAdmin(ModelView, model=Parent):
    # Define columns to display in the admin view
    column_list = [Parent.id, Parent.name, Parent.email, Parent.children]

class ChildAdmin(ModelView, model=Child):
    # Define columns to display in the admin view
    column_list = [Child.id, Child.name, Child.parent_id, Child.parent]

admin.add_view(ParentAdmin)
admin.add_view(ChildAdmin)
