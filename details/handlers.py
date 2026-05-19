from telegram import Update, InlineKeyboardMarkup, ReplyKeyboardMarkup, InputMediaDocument
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes
)
from telegram.error import BadRequest
from settings import *
from details.database.db import *
from .messages import *
from .buttons import *

async def log_deleter(type, user_id, context):
    messages = []

    for t in type:
        messages += context.user_data.get(t, [])

    for msg_id in messages:
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
        except BadRequest:
            pass

    for t in type:
        context.user_data[t] = []

async def log_adder(type, msg_id, context):
    for m in msg_id:
        context.user_data.setdefault(str(type), []).append(m)

import requests
from datetime import datetime


def hr_message():
    # 🔗 URL ni o‘zing shu yerga qo‘yasan
    URL = "https://mirmaks-davomat-server.onrender.com/api/hr/getall"

    res = requests.get(URL, timeout=15)
    data = res.json()

    if not data.get("success"):
        return "❌ Ma'lumot olishda xatolik yuz berdi."

    date = data.get("date", "")
    employees = data.get("data", [])
    total = data.get("total", len(employees))

    # 📊 counters
    present = 0
    absent = 0

    rows = []

    for i, emp in enumerate(employees, start=1):

        name = emp.get("fullname", "Noma'lum")
        position = emp.get("position", "-")
        active = emp.get("active", False)
        came = emp.get("came", False)
        arrival = emp.get("arrival_time")
        leave = emp.get("leave_time")

        # STATUS LOGIC
        if came:
            status = "🟢 KELGAN"
            present += 1
        else:
            status = "🔴 KELMAGAN"
            absent += 1

        arrival = arrival if arrival else "-"
        leave = leave if leave else "-"

        rows.append(
            f"{i}. {name} | {position}\n"
            f"   🕒 Kirish: {arrival} | Chiqish: {leave}\n"
            f"   📌 Holat: {status}\n"
        )

    # 📌 HEADER
    message = (
        f"🏢 <b>HR DAVOMAT HISOBOTI</b>\n"
        f"📅 Sana: <b>{date}</b>\n\n"
        f"👥 Jami xodimlar: <b>{total}</b>\n"
        f"🟢 Kelganlar: <b>{present}</b>\n"
        f"🔴 Kelmaganlar: <b>{absent}</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    message += "\n".join(rows)

    message += (
        "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 Kadrlar bo'limi menejeri: @mirmaks_kadr\n"
        "⚙️ Dasturchi: @BroAzik\n"
    )

    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.full_name

    user = get(table="users", user_id=user_id)

    if user_id == ADMIN_ID: 
        if not user:
            insert(
                user_id=user_id,
                table="users",
                data={
                    "first_name": name,
                    "user_id": user_id,
                    "role": "Admin",
                    "stage": "start",
                    "index": 0,
                    "logged_in": True,
                    "position": "Admin",
                    "active": True
                    }
                )
        else:
            upd(table="users", data={"role":"Admin", "logged_in": True, "stage": "start"}, user_id=user_id)
        
        msg = await update.message.reply_text(
                    text=ADMIN_welcome_mes,
                    reply_markup=ReplyKeyboardMarkup(
                        ADMIN_start_but,
                        resize_keyboard=True)
                        )

    else:
        if not user:
            insert(
                user_id=user_id,
                table="users",
                data={
                    "first_name": name,
                    "user_id": user_id,
                    "role": "User",
                    "stage": "start",
                    "index": 0,
                    "logged_in": False,
                    "position": "",
                    "active": True
                    }
                )
            msg = await update.message.reply_text(
                    text=USER_start_mes,
                    parse_mode=ParseMode.HTML
                    )
        else:
            if user["role"] == "Employee":
                upd(table="users", data={"logged_in": True, "stage": "start"}, user_id=user_id)

                msg = await update.message.reply_text(
                    text=EMPLOYEE_start_mes.format(user["first_name"], user["position"]),
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(WebApp_start_but(user_id)))
            else:
                msg = await update.message.reply_text(
                    text=USER_start_mes,
                    parse_mode=ParseMode.HTML
                    )
    
    await log_deleter(type=["start", "messages"], user_id=user_id, context=context)
    await log_adder(type="start", msg_id=[update.message.message_id, msg.message_id], context=context)

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "view_attendance":
        report_message = hr_message()
        await query.answer()
        try:
            await query.edit_message_text(text=report_message, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(WebApp_start_but(user_id)))
        except:
            await query.answer(text="Boshqa ma'lumotlar topilmadi.")

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get(table="users", user_id=user_id)
    stage = user["stage"]
    messaage = update.message.text

    if user_id == ADMIN_ID: 
        if user["stage"] == "start":
            if messaage == "Xodimlar ro'yxati":
                employees = get(table="users")
                text = ADMIN_list_mes1
                for i, emp in enumerate(employees, start=1):
                    if emp["role"] != "User":
                        text += ADMIN_list_mes2.format(i, emp["user_id"], emp["first_name"], emp["position"], "Ha" if emp["active"] else "Yo'q")
                msg = await update.message.reply_text(text=text, parse_mode=ParseMode.HTML)
            
            if messaage == "Xodim qo'shish":
                upd(table="users", data={"stage": "get_id"}, user_id=user_id)
                msg = await update.message.reply_text(text=get_employe_id_mes)
            
            if messaage == "Xodimni o'chirish":
                upd(table="users", data={"stage": "get_id_delete"}, user_id=user_id)
                msg = await update.message.reply_text(text=get_employe_id_mes)

        if stage == "get_id":
                if messaage.isdigit():
                    upd(table="users", data={"stage": "get_name", "index": int(messaage)}, user_id=user_id)
                    msg = await update.message.reply_text(text=get_employe_name_mes)
                else:
                    msg = await update.message.reply_text(text="Iltimos, raqam kiriting.")

        if stage == "get_id_delete":
            if messaage.isdigit():
                try:
                    delete(table="users", user_id=int(messaage))
                    msg = await update.message.reply_text(text=f"{messaage} ID raqamli xodim muvaffaqiyatli o'chirildi.")
                except:
                    msg = await update.message.reply_text(text=f"{messaage} ID raqamli xodim topilmadi.")
            else:
                msg = await update.message.reply_text(text="Iltimos, raqam kiriting.")

        if stage == "get_name":
                upd(table="users", data={"stage": "get_position", "name": messaage}, user_id=user_id)
                msg = await update.message.reply_text(text=get_employe_position_mes)

        if stage == "get_position":
                index = user["index"]
                name = user["name"]
                position = messaage
                insert(
                    table="users",
                    user_id=index,
                    data={
                        "first_name": name,
                        "user_id": index,
                        "role": "Employee",
                        "stage": "start",
                        "index": 0,
                        "logged_in": False,
                        "position": position,
                        "active": True
                    }
                )
                upd(table="users", data={"stage": "start"}, user_id=user_id)
                await log_adder(type="messages", msg_id=[update.message.message_id], context=context)
                await log_deleter(type=["messages"], user_id=user_id, context=context)
                msg = await update.message.reply_text(text=f"{name} ismli xodim muvaffaqiyatli qo'shildi.")

    await log_deleter(type=["messages"], user_id=user_id, context=context)
    await log_adder(type="messages", msg_id=[update.message.message_id, msg.message_id], context=context)
