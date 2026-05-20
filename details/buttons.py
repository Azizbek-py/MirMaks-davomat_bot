from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from settings import WEB_APP_URL

ADMIN_start_but = [
    ["Xodimlar ro'yxati"],
    ["Xodim qo'shish", "Xodimni o'chirish"],
]


def WebApp_start_but(user_id):
    url = f"{WEB_APP_URL}?user_id={user_id}"

    result = [[
                
                InlineKeyboardButton(
                    text="Davomatni ko'rish👀",
                    callback_data="view_attendance"
                    )
            ],
            [
                InlineKeyboardButton(
                    text="Davomat",
                        url=url
                    
                )
            ]
        ]
    return result
