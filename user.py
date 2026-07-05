from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from database import add_user, get_channels
from keyboards import subscribe_keyboard, main_menu_keyboard

user_router = Router()


async def get_not_subscribed_channels(bot: Bot, user_id: int) -> list:
    """Foydalanuvchi hali obuna bo'lmagan kanal/guruhlar ro'yxatini qaytaradi."""
    channels = await get_channels()
    not_subscribed = []
    for chat_id, title, username, invite_link, chat_type in channels:
        try:
            member = await bot.get_chat_member(chat_id, user_id)
            if member.status in ("left", "kicked"):
                not_subscribed.append((chat_id, title, username, invite_link, chat_type))
        except TelegramBadRequest:
            # Bot bu chatda admin emas yoki chat topilmadi - tekshirmasdan o'tkazamiz
            continue
    return not_subscribed


@user_router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    await add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name
    )

    not_subscribed = await get_not_subscribed_channels(bot, message.from_user.id)

    if not_subscribed:
        await message.answer(
            "👋 Assalomu alaykum!\n\n"
            "Botdan foydalanish uchun quyidagi kanal/guruh(lar)ga obuna bo'ling, "
            "so'ngra <b>✅ Tekshirish</b> tugmasini bosing:",
            reply_markup=subscribe_keyboard(not_subscribed)
        )
    else:
        await message.answer(
            "✅ Xush kelibsiz! Quyidagi menyudan foydalanishingiz mumkin:",
            reply_markup=main_menu_keyboard()
        )


@user_router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, bot: Bot):
    not_subscribed = await get_not_subscribed_channels(bot, callback.from_user.id)

    if not_subscribed:
        await callback.answer(
            "❌ Siz hali barcha kanal/guruhlarga obuna bo'lmadingiz!",
            show_alert=True
        )
        try:
            await callback.message.edit_reply_markup(reply_markup=subscribe_keyboard(not_subscribed))
        except TelegramBadRequest:
            pass
    else:
        await callback.message.delete()
        await callback.message.answer(
            "✅ Rahmat! Endi botdan to'liq foydalanishingiz mumkin:",
            reply_markup=main_menu_keyboard()
        )


# ---------- ASOSIY MENYU TUGMALARI ----------
# Bu yerga o'zingizning funksiyalaringizni qo'shishingiz mumkin

@user_router.message(F.text == "📄 Kod yuboring")
async def send_code(message: Message):
    await message.answer("Bu yerga siz yubormoqchi bo'lgan matn yoki kodni yozing 🙂")


@user_router.message(F.text == "ℹ️ Bot haqida")
async def about_bot(message: Message):
    await message.answer("Bu bot majburiy obuna tizimi bilan ishlaydi. Sozlamalarni admin boshqaradi.")
