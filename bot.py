import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ChatInviteLink, LabeledPrice, ContentType, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
import aiosqlite
from datetime import datetime, timedelta
import hmac
import hashlib
from fastapi import FastAPI, Request



load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
PAYMASTER_TOKEN = os.getenv("PAYMASTER_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

#Кнопка старт
@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить подписку на 30 дней", callback_data="buy_30")],
        [InlineKeyboardButton(text="💳 Купить подписку на 60 дней", callback_data="buy_60")],
        [InlineKeyboardButton(text="💳 Купить подписку на 90 дней", callback_data="buy_90")],
    ])
    await message.answer("Выбери действие:", reply_markup=kb)

#Подписка на 30 дней
@dp.callback_query(F.data == "buy_30")
async def buy_30(callback: CallbackQuery):
    prices = [LabeledPrice(label="Подписка на 30 дней", amount=5000)]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Подписка на канал",
        description="Доступ на 30 дней",
        payload="sub_30",
        provider_token=PAYMASTER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="sub-start",
    )
    await callback.answer() # закрыть "часики" на кнопке

#Подписка на 60 дней
@dp.callback_query(F.data == "buy_60")
async def buy_60(callback: CallbackQuery):
    prices = [LabeledPrice(label="Подписка на 60 дней", amount=10000)]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Подписка на канал",
        description="Доступ на 60 дней",
        payload="sub_60",
        provider_token=PAYMASTER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="sub-start",
    )
    await callback.answer()

#Подписка на 90 дней
@dp.callback_query(F.data == "buy_90")
async def buy_90(callback: CallbackQuery):
    prices = [LabeledPrice(label="Подписка на 90 дней", amount=15000)]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Подписка на канал",
        description="Доступ на 90 дней",
        payload="sub_90",
        provider_token=PAYMASTER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="sub-start",
    )
    await callback.answer()

#Проверка оплаты
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

#Успешная оплата
@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    payload = message.successful_payment.invoice_payload

    if payload == "sub_30":
        expire_at = await add_sub(message.from_user.id, seconds=30)
        #expire_at = await add_sub(message.from_user.id, days=30)
        await message.answer(f"✅ Оплата прошла! Подписка до {expire_at.date()}")
    elif payload == "sub_60":
        expire_at = await add_sub(message.from_user.id, days=60)
        await message.answer(f"✅ Оплата прошла! Подписка до {expire_at.date()}")
    elif payload == "sub_90":
        expire_at = await add_sub(message.from_user.id, days=90)
        await message.answer(f"✅ Оплата прошла! Подписка до {expire_at.date()}")
    invite = await bot.create_chat_invite_link(chat_id=GROUP_ID, member_limit=1)
    await message.answer(f"Ваша ссылка для входа: {invite.invite_link}")





#Сохранение подписок
async def add_sub(user_id: int, days: int):
    expire_at = datetime.utcnow() + timedelta(days=days)
    async with aiosqlite.connect("db.sqlite") as db:
        await db.execute(
            "INSERT INTO subscriptions (user_id, group_id, expire_at) VALUES(?, ?, ?)",
            (user_id, GROUP_ID, expire_at.isoformat())
        )
        await db.commit()
    return expire_at

#Проверка и удаление просроченных
async def chek_sub():
    now = datetime.utcnow()
    async with aiosqlite.connect("db.sqlite") as db:
        async with db.execute(
            "SELECT user_id, group_id, expire_at FROM subscriptions"
        ) as cursor:
            rows = await cursor.fetchall()
            for user_id, group_id, expire_at in rows:
                if datetime.fromisoformat(expire_at) < now:
                    try:
                        await bot.ban_chat_member(group_id, user_id)
                        await bot.unban_chat_member(group_id, user_id)

                    except Exception as e:
                        print(f"Ошибка ри удалении {user_id}: {e}")
                    await db.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
                    db.commit()




@dp.pre_checkout_query()
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)



#Проверка при старте
async def sub_chec():
    while True:
        await chek_sub()
        await asyncio.sleep(60)

async def main():
    asyncio.create_task(sub_chec())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())