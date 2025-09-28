import hmac
import hashlib
from fastapi import FastAPI, Request

app = FastAPI()

SECRET_KEY = "7419363103:AAEKXI3m5u9JQIgOJ5qvj_6ZHKdizpI6aIU"

def verify_sig(data: dict, signature: str) -> bool:
    paylod = "&".join(f"{k}={v}" for k, v in sorted(data.items()))
    calc_signature = hmac.new(
        SECRET_KEY.encode(),
        paylod.encode(),
        hashlib.sha256
    ).hexdigest()
    return calc_signature == signature

@app.post("/paymaster-webhook")
async def paymaster(request: Request):
    data = await request.json()
    signature = data.pop("signature", "")
    if not verify_sig(data, signature):
        return {"status": "error", "message": "bad signature"}

    if data.get("paymentStatus") == "success":
        user_id = int(data["user_id"])
        await add_sub(user_id, days=30)
        expire_at = await add_sub(user_id, days=30)

        await bot.send_message(user_id, f"✅ Подписка оформлена до {expire_at.date()}")

        invite = await bot.create_chat_invite_link(chat_id=CHANNEL_ID, member_limit=1)
        await bot.send_message(user_id, f"Ваша ссылка для входа: {invite.invite_link}")

    return {"ok": True}