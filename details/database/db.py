from tinydb import TinyDB, Query
from tinydb.database import Document
import httpx
import asyncio

db = TinyDB('details/database/base.json', indent=4)
users = db.table("users")
query = Query()

# ─── SERVER URL ───────────────────────────────────────────────────────────────
SERVER_URL = "https://mirmaks-davomat-server.onrender.com"

# ─── SERVER SINXRONIZATSIYA (async, event loop ni bloklamaydi) ────────────────
async def _async_sync_add(telegram_id: int, fullname: str, position: str):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(
                f"{SERVER_URL}/api/employees",
                json={
                    "telegram_id": telegram_id,
                    "fullname":    fullname,
                    "position":    position,
                    "active":      True,
                }
            )
        if res.status_code in (200, 400):
            print(f"[SYNC ✓] Qo'shildi: {fullname} ({telegram_id})")
        else:
            print(f"[SYNC ✗] {res.status_code}: {res.text}")
    except Exception as e:
        print(f"[SYNC ✗] {e}")


async def _async_sync_delete(telegram_id: int):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.delete(f"{SERVER_URL}/api/employees/{telegram_id}")
        if res.status_code in (200, 404):
            print(f"[SYNC ✓] O'chirildi: {telegram_id}")
        else:
            print(f"[SYNC ✗] {res.status_code}: {res.text}")
    except Exception as e:
        print(f"[SYNC ✗] {e}")


async def _async_sync_update(telegram_id: int, data: dict):
    update_fields = {}
    if "first_name" in data: update_fields["fullname"]  = data["first_name"]
    if "position"   in data: update_fields["position"]  = data["position"]
    if "active"     in data: update_fields["active"]    = data["active"]
    if not update_fields:
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.put(
                f"{SERVER_URL}/api/employees/{telegram_id}",
                json=update_fields
            )
        if res.status_code == 200:
            print(f"[SYNC ✓] Yangilandi: {telegram_id}")
        else:
            print(f"[SYNC ✗] {res.status_code}: {res.text}")
    except Exception as e:
        print(f"[SYNC ✗] {e}")


def _fire_async(coro):
    """
    Sinxron funksiya ichidan async task ishga tushiradi.
    Event loop ni bloklamaydi — bot ishlashda davom etadi.
    """
    try:
        loop = asyncio.get_running_loop()
        # Async muhit ichida — task sifatida qo'shamiz
        loop.create_task(coro)
    except RuntimeError:
        # Async muhit yo'q — yangi loop ochib ishlatamiz
        asyncio.run(coro)


# ─── ASOSIY FUNKSIYALAR ───────────────────────────────────────────────────────
def get(table, user_id=None):
    if table == "users":
        if user_id is None:
            return users.all()
        else:
            return users.get(doc_id=user_id)


def insert(table, data, user_id=None):
    if table == "users":
        if user_id is not None:
            user_id  = int(user_id)
            existing = users.get(doc_id=user_id)
            if existing:
                users.update(data, doc_ids=[user_id])
            else:
                doc = Document(value=data, doc_id=user_id)
                users.insert(doc)

            # Faqat Employee qo'shilganda serverga yuboramiz
            role = data.get("role", existing.get("role", "") if existing else "")
            if role == "Employee":
                fullname = data.get("first_name", "")
                position = data.get("position", "")
                if fullname and position:
                    _fire_async(_async_sync_add(user_id, fullname, position))
        else:
            users.insert(data)


def upd(table, data, user_id=None):
    if table == "users" and user_id is not None:
        user_id = int(user_id)
        users.update(data, doc_ids=[user_id])

        if any(k in data for k in ("position", "active", "first_name")):
            user = users.get(doc_id=user_id)
            if user and user.get("role") == "Employee":
                _fire_async(_async_sync_update(user_id, data))


def delete(table, user_id=None):
    if table == "users" and user_id is not None:
        user_id = int(user_id)
        user    = users.get(doc_id=user_id)
        users.remove(doc_ids=[user_id])

        if user and user.get("role") == "Employee":
            _fire_async(_async_sync_delete(user_id))
