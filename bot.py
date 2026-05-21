from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import json

TOKEN = "8940821525:AAFo0KhYpTSw1vPJ6kdYQrjBDoAAbhtXxX0"

ADMIN_CHAT_ID = -1003426381344

bot = Bot(token=TOKEN)
dp = Dispatcher()

with open("violations.json", "r") as f:
    violations = json.load(f)

user_data = {}


@dp.message()
async def all_messages(message: types.Message):

    text = message.text.strip()

    # =========================
    # START
    # =========================

    if text == "/start":

        await message.answer(
    "🚛 Welcome to Muxammad's FMCSA Bot\n\n"
    "Send violation code or search keyword.\n\n"

    "Examples:\n"
    "392.2R\n"
    "392.80(a)\n"
    "392.2P\n"
    "392.2Y\n\n"

    "You can also search by violation name:\n"
    "speeding\n"
    "seat belt\n"
    "railroad crossing"
)

        return

    # =========================
    # HELP
    # =========================

    if text == "/help":

        await message.answer(
            "🛠 FMCSA Bot Help\n\n"
            "Send violation code or keyword.\n\n"
            "Examples:\n"
            "392.2R\n"
            "speeding\n"
            "seat belt"
        )

        return

    # =========================
    # TOP
    # =========================

    if text == "/topviolations":

        await message.answer(
            "🔥 Top Violations\n\n"
            "392.2-SLLS4 — Speeding 15+\n"
            "392.2R — Reckless driving\n"
            "392.80(a) — Texting\n"
            "392.82(a)(1) — Handheld phone\n"
            "392.16 — No seat belt"
        )

        return

    # =========================
    # ADVICE
    # =========================

    if text == "/advice":

        await message.answer(
            "🧠 CSA Safety Advice\n\n"
            "✅ Avoid speeding\n"
            "✅ Wear seat belts\n"
            "✅ No handheld phones\n"
            "✅ Keep logs accurate\n"
            "✅ Inspect vehicles daily"
        )

        return

    # =========================
    # SEARCH
    # =========================

    matches = []

    for key in violations:

        if (
            text.upper() in key.upper()
            or text.lower() in violations[key]["description"].lower()
        ):

            matches.append(key)

    # =========================
    # PARTIAL SEARCH
    # =========================

    if len(matches) > 1:

        buttons = []

        for code in matches[:20]:

            buttons.append(
                [
                    InlineKeyboardButton(
                        text=code,
                        callback_data=f"select_{code}"
                    )
                ]
            )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=buttons
        )

        await message.answer(
            "🔎 Select violation:",
            reply_markup=keyboard
        )

        return

    # =========================
    # EXACT SEARCH
    # =========================

    if text in violations:

        user_data[message.from_user.id] = text

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="0-6 Months",
                        callback_data="x3"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="6-12 Months",
                        callback_data="x2"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="12-24 Months",
                        callback_data="x1"
                    )
                ]
            ]
        )

        await message.answer(
            "Select violation age:",
            reply_markup=keyboard
        )

        return

    await message.answer(
        "❌ Violation not found"
    )


@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):

    # =========================
    # SELECT VIOLATION
    # =========================

    if callback.data.startswith("select_"):

        code = callback.data.replace("select_", "")

        user_data[callback.from_user.id] = code

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="0-6 Months",
                        callback_data="x3"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="6-12 Months",
                        callback_data="x2"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="12-24 Months",
                        callback_data="x1"
                    )
                ]
            ]
        )

        await callback.message.answer(
            f"📌 Selected violation: {code}\n\nSelect violation age:",
            reply_markup=keyboard
        )

        await callback.answer()

        return

    # =========================
    # FEEDBACK
    # =========================

    if callback.data in ["accurate", "review", "incorrect"]:

        await bot.send_message(
            ADMIN_CHAT_ID,
            f"""
🚨 New Feedback

👤 User: {callback.from_user.id}

📊 Feedback: {callback.data}
"""
        )

        await callback.answer(
            "✅ Feedback received"
        )

        return

    # =========================
    # CSA CALCULATION
    # =========================

    code = user_data.get(callback.from_user.id)

    if not code:
        return

    violation = violations[code]

    severity = violation["severity"]

    if callback.data == "x3":

        total = severity * 3
        age = "0-6 Months"

    elif callback.data == "x2":

        total = severity * 2
        age = "6-12 Months"

    else:

        total = severity
        age = "12-24 Months"

    feedback_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Accurate",
                    callback_data="accurate"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚠️ Needs Review",
                    callback_data="review"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Incorrect",
                    callback_data="incorrect"
                )
            ]
        ]
    )

    await callback.message.answer(
        f"🚛 FMCSA CSA Violation Result\n\n"

        f"📌 Code: {code}\n"
        f"📖 Violation: {violation['description']}\n\n"

        f"⚠️ BASIC: {violation['basic']}\n"
        f"📂 Group: {violation['group']}\n\n"

        f"🎯 Severity Weight: {severity}\n"
        f"📅 Violation Age: {age}\n\n"

        f"🔥 Total CSA Points: {total}",

        reply_markup=feedback_keyboard
    )

    await callback.answer()


async def main():

    print("Bot started...")

    await dp.start_polling(bot)


asyncio.run(main())