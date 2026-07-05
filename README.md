# Majburiy obuna (Force-Subscribe) Telegram bot

## 1. O'rnatish

```bash
pip install -r requirements.txt
```

## 2. Sozlash

`config.py` faylini oching:

```python
BOT_TOKEN = "SIZNING_BOT_TOKENINGIZ"   # @BotFather dan oling
ADMIN_IDS = [123456789]                # @userinfobot orqali o'z ID ingizni bilib oling
```

## 3. Ishga tushirish

```bash
python main.py
```

## 4. Foydalanish

### Foydalanuvchi tomoni
- `/start` — bot ishga tushadi, majburiy kanal/guruhlarga obunani tekshiradi
- Obuna bo'lmagan bo'lsa — kanal/guruh tugmalari va "✅ Tekshirish" tugmasi chiqadi
- Hammasiga obuna bo'lgach — asosiy menyu ochiladi

### Admin tomoni — `/admin`
- **➕ Kanal/Guruh qo'shish** — avval botni kerakli kanal/guruhga **admin** qilib qo'shing,
  so'ng o'sha yerdan istalgan xabarni botga forward qiling
- **📃 Kanallar ro'yxati** — qo'shilgan kanal/guruhlarni ko'rish va o'chirish
- **📊 Statistika** — foydalanuvchilar va kanallar soni
- **📢 Xabar yuborish** — barcha foydalanuvchilarga xabar (matn/rasm/video) yuborish

## Muhim eslatmalar

- Bot **kanal**ga qo'shilganda: "Add Admins" orqali admin qiling
- Bot **guruh**ga qo'shilganda: guruh sozlamalaridan "Administrators" bo'limiga qo'shing
- Botga kamida quyidagi huquqlarni bering:
  - A'zolarni ko'rish (obuna tekshirish uchun)
  - Taklif havolasi yaratish (agar kanal/guruh yopiq/username'siz bo'lsa)
- Menyu tugmalari (`handlers/user.py` ichida `📄 Kod yuboring` va h.k.) — bu
  namuna. O'zingizning kerakli funksiyalaringizni shu yerga qo'shishingiz mumkin.

## Loyiha tuzilmasi

```
telegram_forcesub_bot/
├── main.py            # botni ishga tushiruvchi fayl
├── config.py           # token va admin ID lar
├── database.py          # SQLite bilan ishlash
├── keyboards.py          # tugmalar (inline/reply)
├── requirements.txt
└── handlers/
    ├── user.py          # /start va foydalanuvchi menyusi
    └── admin.py          # /admin panel, broadcast, kanal boshqaruvi
```
