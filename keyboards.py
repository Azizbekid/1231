from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def subscribe_keyboard(channels):
    """channels: [(chat_id, title, username, invite_link, chat_type), ...]"""
    builder = InlineKeyboardBuilder()
    for chat_id, title, username, invite_link, chat_type in channels:
        url = f"https://t.me/{username}" if username else invite_link
        builder.button(text=f"➕ {title}", url=url)
    builder.button(text="✅ Tekshirish", callback_data="check_subscription")
    builder.adjust(1)
    return builder.as_markup()


def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📄 Kod yuboring")
    builder.button(text="ℹ️ Bot haqida")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def admin_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Kanal/Guruh qo'shish", callback_data="admin_add_channel")
    builder.button(text="📃 Kanallar ro'yxati", callback_data="admin_list_channels")
    builder.button(text="📊 Statistika", callback_data="admin_stats")
    builder.button(text="📢 Xabar yuborish (Broadcast)", callback_data="admin_broadcast")
    builder.adjust(1)
    return builder.as_markup()


def cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Bekor qilish", callback_data="admin_cancel")
    return builder.as_markup()


def channels_remove_keyboard(channels):
    builder = InlineKeyboardBuilder()
    for chat_id, title, username, invite_link, chat_type in channels:
        builder.button(text=f"🗑 {title}", callback_data=f"remove_ch_{chat_id}")
    builder.button(text="⬅️ Orqaga", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()
