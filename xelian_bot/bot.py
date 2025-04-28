import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# === Настройки ===
TOKEN = "7657060900:AAFgnNmu1fYG8StMN4f1klc4OQ63-Ivk6iI"  # токен бота
ADMIN_CHAT_ID = 6296953786  # твой Telegram ID

# === Инициализация ===
bot = Bot(token=TOKEN)
dp = Dispatcher()

# === Память состояний и анкет ===
user_state = {}
user_answers = {}

# === Клавиатуры ===
start_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Получить анкету", callback_data="get_form")]
    ]
)

def admin_kb(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{user_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_{user_id}")
            ]
        ]
    )

# === Хендлеры ===

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! Чтобы вступить во флуд нажми на «Получить анкету»",
        reply_markup=start_kb
    )

@dp.message(Command("get_id"))
async def get_chat_id(message: types.Message):
    chat = message.chat
    await message.answer(
        f"👑 Информация о чате:\n\n"
        f"📍 Chat ID: `{chat.id}`\n"
        f"📍 Название: {chat.title or 'Личка/Приватный чат'}\n"
        f"📍 Тип чата: {chat.type}",
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "get_form")
async def send_form(callback_query: types.CallbackQuery):
    await callback_query.message.answer(
        """Анкета:
• Возраст
• Актив/Неактив
• Смотрел(-а) аниме/читал(-а) новеллу/манвху/все вместе?
• Готов(-а) к бесконечному веселью и вайбу?
• Роль, за которую хочешь зайти

✍️ Отправьте свои ответы одним сообщением."""
    )
    user_state[callback_query.from_user.id] = "waiting_for_form"
    await callback_query.answer()

@dp.message()
async def handle_form(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_state and user_state[user_id] == "waiting_for_form":
        user_answers[user_id] = message.text

        # Отправка анкеты админу
        await bot.send_message(
            ADMIN_CHAT_ID,
            f"Новая анкета от @{message.from_user.username or message.from_user.first_name}:\n\n{message.text}",
            reply_markup=admin_kb(user_id)
        )

        await message.answer("Ваша анкета на рассмотрении, вам напишут в ближайшее время🦋")
        user_state.pop(user_id)

@dp.callback_query(F.data.startswith(("accept_", "decline_")))
async def admin_decision(callback_query: types.CallbackQuery):
    action, user_id = callback_query.data.split("_")
    user_id = int(user_id)

    if action == "accept":
        try:
            # Создаем одноразовую ссылку
            invite_link = await bot.create_chat_invite_link(
                chat_id=GROUP_CHAT_ID,
                member_limit=1,
                creates_join_request=False
            )

            # Красивая кнопка для перехода
            join_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🌸 Перейти во флуд", url=invite_link.invite_link)]
                ]
            )

            await bot.send_message(
                user_id,
                "🌟 Поздравляем! Ваша анкета принята! Добро пожаловать в «Царство Се Ляня»! 🌸\n\n"
                "🔮 Вас ждёт бесконечное веселье, дружба и уютный вайб.\n\n"
                "⚡ Внимание: ссылка одноразовая, успей присоединиться!",
                reply_markup=join_kb
            )
        except Exception as e:
            await bot.send_message(ADMIN_CHAT_ID, f"❗ Ошибка создания ссылки: {e}")

    elif action == "decline":
        await bot.send_message(
            user_id,
            "❌ К сожалению, ваша анкета отклонена.\n"
            "✨ Вы можете попробовать снова позже!"
        )

    await callback_query.answer("Решение отправлено пользователю!")

# === Запуск бота ===
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
