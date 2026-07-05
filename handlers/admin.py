import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from config import ADMIN_IDS
from database import (
    add_channel, remove_channel, get_channels,
    channels_count, users_count, get_all_users
)
from keyboards import admin_menu_keyboard, cancel_keyboard, channels_remove_keyboard
from git_sync import sync_database_to_github

admin_router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


class AdminStates(StatesGroup):
    waiting_channel = State()
    waiting_broadcast = State()


@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🛠 Admin panel:", reply_markup=admin_menu_keyboard())


@admin_router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("🛠 Admin panel:", reply_markup=admin_menu_keyboard())


@admin_router.callback_query(F.data == "admin_cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.clear()
    await callback.message.edit_text("🛠 Admin panel:", reply_markup=admin_menu_keyboard())


# ============================================================
# KANAL / GURUH QO'SHISH
# ============================================================

@admin_router.callback_query(F.data == "admin_add_channel")
async def admin_add_channel(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.waiting_channel)
    await callback.message.edit_text(
        "📌 <b>Qadamlar:</b>\n"
        "1. Botni kerakli kanal yoki guruhga qo'shing\n"
        "2. Botga <b>admin</b> huquqini bering (a'zolarni ko'rish va "
        "taklif havolasi yaratish huquqlari bilan)\n"
        "3. O'sha kanal/guruhdagi istalgan bir xabarni shu yerga "
        "<b>forward</b> qiling\n",
        reply_markup=cancel_keyboard()
    )


@admin_router.message(AdminStates.waiting_channel)
async def process_add_channel(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    chat = message.forward_from_chat
    if chat is None:
        await message.answer(
            "⚠️ Iltimos, kanal yoki guruhdan xabarni <b>forward</b> qiling (shaxsdan emas).",
            reply_markup=cancel_keyboard()
        )
        return

    try:
        bot_member = await bot.get_chat_member(chat.id, bot.id)
    except TelegramBadRequest:
        await message.answer(
            "❌ Bot bu chatda topilmadi. Avval botni o'sha kanal/guruhga qo'shing.",
            reply_markup=cancel_keyboard()
        )
        return

    if bot_member.status not in ("administrator", "creator"):
        await message.answer(
            "❌ Bot ushbu kanal/guruhda admin emas. Botga admin huquqini bering "
            "va qaytadan forward qiling.",
            reply_markup=cancel_keyboard()
        )
        return

    invite_link = ""
    if not chat.username:
        try:
            invite_link = await bot.export_chat_invite_link(chat.id)
        except TelegramBadRequest:
            await message.answer(
                "❌ Botda taklif havolasi (invite link) yaratish huquqi yo'q. "
                "Botga to'liq admin huquqlarini bering va qaytadan urinib ko'ring.",
                reply_markup=cancel_keyboard()
            )
            return

    chat_type = "channel" if chat.type == "channel" else "group"
    await add_channel(chat.id, chat.title, chat.username or "", invite_link, chat_type)
    await state.clear()

    await sync_database_to_github(f"Kanal/guruh qo'shildi: {chat.title}")

    await message.answer(f"✅ \"{chat.title}\" majburiy obuna ro'yxatiga qo'shildi!")
    await message.answer("🛠 Admin panel:", reply_markup=admin_menu_keyboard())


# ============================================================
# KANALLAR RO'YXATI / O'CHIRISH
# ============================================================

@admin_router.callback_query(F.data == "admin_list_channels")
async def admin_list_channels(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    channels = await get_channels()
    if not channels:
        await callback.answer("Hozircha kanal/guruh qo'shilmagan.", show_alert=True)
        return
    await callback.message.edit_text(
        "📃 Majburiy obuna kanal/guruhlari (o'chirish uchun bosing):",
        reply_markup=channels_remove_keyboard(channels)
    )


@admin_router.callback_query(F.data.startswith("remove_ch_"))
async def admin_remove_channel(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    chat_id = int(callback.data.replace("remove_ch_", ""))
    await remove_channel(chat_id)
    await sync_database_to_github(f"Kanal/guruh o'chirildi: {chat_id}")
    channels = await get_channels()
    if channels:
        await callback.message.edit_text(
            "📃 Majburiy obuna kanal/guruhlari (o'chirish uchun bosing):",
            reply_markup=channels_remove_keyboard(channels)
        )
    else:
        await callback.message.edit_text(
            "Ro'yxat bo'sh.\n\n🛠 Admin panel:",
            reply_markup=admin_menu_keyboard()
        )
    await callback.answer("🗑 O'chirildi")


# ============================================================
# STATISTIKA
# ============================================================

@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    u_count = await users_count()
    c_count = await channels_count()
    await callback.answer()
    await callback.message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👤 Foydalanuvchilar soni: {u_count}\n"
        f"📢 Majburiy kanal/guruhlar soni: {c_count}"
    )


# ============================================================
# BROADCAST (HAMMAGA XABAR YUBORISH)
# ============================================================

@admin_router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.waiting_broadcast)
    await callback.message.edit_text(
        "📢 Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring "
        "(matn, rasm, video — qanday bo'lsa, o'shanday yuboriladi):",
        reply_markup=cancel_keyboard()
    )


@admin_router.message(AdminStates.waiting_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    users = await get_all_users()
    status_msg = await message.answer(f"⏳ Yuborilmoqda... (0/{len(users)})")

    success, failed = 0, 0
    for i, user_id in enumerate(users, start=1):
        try:
            await message.copy_to(user_id)
            success += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            failed += 1

        if i % 20 == 0:
            await asyncio.sleep(1)  # Telegram flood-limitidan saqlanish uchun

    await status_msg.edit_text(
        f"✅ Xabar yuborish yakunlandi!\n\n"
        f"📤 Muvaffaqiyatli: {success}\n"
        f"❌ Yuborilmadi: {failed}"
    )
    await message.answer("🛠 Admin panel:", reply_markup=admin_menu_keyboard())
