from tinydb import TinyDB, Query
from tinydb.database import Document

db = TinyDB('details/database/base.json', indent=4)
users = db.table("users")
query = Query()

def get(table, user_id=None):
    if table == "users":
        if user_id is None:
            return users.all()
        else:
            return users.get(doc_id=user_id)

def insert(table, data, user_id=None):
    if table == "users":
        if user_id is not None:
            user_id = int(user_id)
            existing = users.get(doc_id=user_id)
            if existing:
                users.update(data, doc_ids=[user_id])
            else:
                doc = Document(value=data, doc_id=user_id)
                users.insert(doc)
        else:
            users.insert(data)

def upd(table, data, user_id=None):
    if table == "users" and user_id is not None:
        user_id = int(user_id)
        users.update(data, doc_ids=[user_id])
#         users.remove(doc_ids=[user_id])
#         try:
#             tasks.remove(Query().own_of_file == user_id)
#         except:
#             pass
    # if table == "tasks":
    #     tasks.remove(Query().uniq_id == user_id)

def delete(table, user_id=None):
    if table == "users" and user_id is not None:
        user_id = int(user_id)
        users.remove(doc_ids=[user_id])