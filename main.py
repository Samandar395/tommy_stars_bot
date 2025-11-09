# ⚙️ Sozlamalar
BOT_TOKEN = "7436784296:AAHtXbOln0sS4r8qWBaTUUnXWSE-d9Mdz8E"
ADMIN_ID = 7881879285
CHANNELS = ["@hd_tommy", "@kotta_bolacha"]
PAYMENTS_CHANNEL = "@kotta_bolacha"
REF_BONUS = 3  # referal uchun mukofot

# 📦 Ma’lumotlarni saqlash uchun
users = {}
balance = {}
refs = {}
withdraws = {}

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()


# 🧩 Holatlar
class WithdrawState(StatesGroup):
    amount = State()
    user_id = State()


# 📲 Raqam so‘rash uchun klaviatura
ask_contact = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📱 Raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


# 🔘 Asosiy menyu
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("💫 Stars ishlash"), KeyboardButton("💵 Stars yechish")],
        [KeyboardButton("👤 Mening hisobim"), KeyboardButton("🏦 To‘lovlar kanali")],
        [KeyboardButton("boshqarish")],
    ],
    resize_keyboard=True
)


# 🧩 Start komandasi
@dp.message(CommandStart())
async def start_cmd(msg: types.Message):
    user_id = msg.from_user.id

    if user_id not in users:
        users[user_id] = {"phone": None}
        balance[user_id] = 0
        refs[user_id] = []
        withdraws[user_id] = 0

    await msg.answer(
        "👋 Salom! Botdan foydalanish uchun iltimos, telefon raqamingizni yuboring:",
        reply_markup=ask_contact
    )


# 📞 Kontakt (raqam) qabul qilish
@dp.message(F.contact)
async def get_contact(msg: types.Message):
    user_id = msg.from_user.id
    phone = msg.contact.phone_number

    if not phone.startswith("+998"):
        await msg.answer("❌ Bu bot faqat O‘zbekiston raqamlari uchun mo‘ljallangan.")
        return

    users[user_id]["phone"] = phone

    # Majburiy kanal
    text = (
        "✅ Raqamingiz qabul qilindi!\n\n"
        "Endi botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling 👇"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanal 1", url=f"https://t.me/{CHANNELS[0][1:]}")],
            [InlineKeyboardButton(text="📢 Kanal 2", url=f"https://t.me/{CHANNELS[1][1:]}")],
            [InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="check_subs")]
        ]
    )
    await msg.answer(text, reply_markup=markup)


# 🔍 Obunani tekshirish
@dp.callback_query(F.data == "check_subs")
async def check_subs(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    for ch in CHANNELS:
        member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
        if member.status not in ("member", "administrator", "creator"):
            await callback.message.answer(f"❌ Siz {ch} kanaliga obuna bo‘lmagansiz.")
            await callback.answer()
            return
    await callback.message.answer("✅ Obuna tasdiqlandi!", reply_markup=main_menu)
    await callback.answer()


# 💫 Stars ishlash (referal)
@dp.message(F.text == "💫 Stars ishlash")
async def earn_stars(msg: types.Message):
    user_id = msg.from_user.id
    ref_link = f"https://t.me/{(await bot.me()).username}?start={user_id}"
    text = (
        "✅ Eyyy! Sizda-chi Telegram stars bormi?!\n\n"
        "➡️ Shu kungacha olmagan bo‘lsangiz, yaxshi qilibsiz. Endi bepulga olishingiz mumkin.\n"
        "➡️ Shunchaki botga start bosing va berilgan havola orqali do‘stlaringizni taklif qiling.\n\n"
        f"🔐 Pastdagi havola orqali do‘stlaringizga ulashing:\n👉 {ref_link}\n\n"
        f"💰 Har bir to‘liq ro‘yxatdan o‘tgan taklifingiz uchun <b>{REF_BONUS} star</b> hisobingizga qo‘shiladi!"
    )
    await msg.answer(text)
  # 💵 Stars yechish (inline tugma bilan)
@dp.message(F.text == "💵 Stars yechish")
async def withdraw(msg: types.Message):
    inline = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("⭐ Stars yechish", callback_data="open_withdraw")]
        ]
    )
    await msg.answer("👇 Quyidagi tugmani bosing:", reply_markup=inline)


# ⭐ Inline bosilganda so‘rov boshlanadi
@dp.callback_query(F.data == "open_withdraw")
async def start_withdraw(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("💫 Necha stars yechmoqchisiz?")
    await state.set_state(WithdrawState.amount)
    await callback.answer()


# 💬 Miqdorni olish
@dp.message(WithdrawState.amount)
async def get_amount(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❌ Iltimos, faqat raqam kiriting.")
        return
    await state.update_data(amount=int(msg.text))
    await msg.answer("🆔 To‘lov uchun ID raqamingizni kiriting:")
    await state.set_state(WithdrawState.user_id)


# 💬 Foydalanuvchi ID kiritadi
@dp.message(WithdrawState.user_id)
async def get_userid(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data["amount"]
    user_id = msg.from_user.id
    user_name = msg.from_user.username or "no_username"

    text_admin = (
        f"💸 <b>Yangi yechish so‘rovi!</b>\n\n"
        f"👤 Foydalanuvchi: @{user_name}\n"
        f"🆔 Telegram ID: <code>{user_id}</code>\n"
        f"📦 To‘lov ID: {msg.text}\n"
        f"💰 Miqdor: {amount}⭐"
    )
    await bot.send_message(ADMIN_ID, text_admin)
    await msg.answer("✅ So‘rovingiz yuborildi, tez orada ko‘rib chiqiladi.")
    await state.clear()


# 🏦 To‘lovlar kanali
@dp.message(F.text == "🏦 To‘lovlar kanali")
async def payments_channel(msg: types.Message):
    inline = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🔗 Kanalga o‘tish", url=f"https://t.me/{PAYMENTS_CHANNEL[1:]}")]
        ]
    )
    await msg.answer("⤵️ Quyidagi kanal orqali to‘lovlarni kuzatib boring:", reply_markup=inline)


# 👤 Mening hisobim
@dp.message(F.text == "👤 Mening hisobim")
async def my_account(msg: types.Message):
    user_id = msg.from_user.id
    text = (
        f"🔑 Sizning ID raqamingiz: <code>{user_id}</code>\n\n"
        f"💵 Asosiy balansingiz: {balance.get(user_id, 0)}⭐\n"
        f"👤 Takliflaringiz soni: {len(refs.get(user_id, []))} ta\n\n"
        f"💳 Yechib olgan ⭐ingiz: {withdraws.get(user_id, 0)} so‘m"
    )
    await msg.answer(text)


# ⚙️ Faqat admin uchun boshqarish
@dp.message(F.text.lower() == "boshqarish")
async def admin_panel(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    text = (
        "⚙️ <b>Admin panel</b>\n\n"
        "Bu yerda siz botni boshqarishingiz, kanal nomlarini yoki mukofot miqdorini o‘zgartirishingiz mumkin."
    )
    await msg.answer(text)


# 🏁 Ishga tushirish
async def main():
    print("✅ Bot ishga tushdi...")
    await dp.start_polling(bot)


if name == "main":
    asyncio.run(main())
