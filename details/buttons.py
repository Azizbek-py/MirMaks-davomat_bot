from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from settings import WEB_APP_URL

ADMIN_start_but = [
    ["Xodimlar ro'yxati"],
    ["Xodim qo'shish", "Xodimni o'chirish"],
]

WebApp_start_but = [
        [
            InlineKeyboardButton(
                text="Davomat",
                web_app=WebAppInfo(
                    url=WEB_APP_URL
                )
            )
        ]
    ]