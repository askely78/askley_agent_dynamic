
import os
from typing import Dict
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from twilio.rest import Client
import openai

app = FastAPI()

# Variables d'environnement
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_WHATSAPP_FROM")  # Format : whatsapp:+14155238886
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
openai.api_key = OPENAI_API_KEY

# Mémoire temporaire des sessions utilisateur
session_memory: Dict[str, Dict[str, str]] = {}

@app.get("/")
def read_root():
    return {"message": "Askley backend with GPT-4.1 is live ✅"}

@app.post("/whatsapp-webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...)
):
    print(f"📥 Message reçu de {From} : {Body}")
    body_lower = Body.lower()

    # Initialiser mémoire si nouveau numéro
    if From not in session_memory:
        session_memory[From] = {}

    # Utiliser GPT-4.1 pour générer la réponse
    try:
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4.0-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant de conciergerie marocaine qui aide à réserver des hôtels, restaurants, plats, produits artisanaux, etc."},
                {"role": "user", "content": Body}
            ],
            max_tokens=150,
            temperature=0.7
        )
        message_texte = gpt_response['choices'][0]['message']['content'].strip()
    except Exception as e:
        message_texte = (
            "👋 Bienvenue chez Askley !
"
            "1️⃣ Réserver un hôtel
"
            "2️⃣ Réserver un restaurant
"
            "3️⃣ Commander un plat
"
            "4️⃣ Produits artisanaux
"
            "5️⃣ Plats faits maison
"
            "6️⃣ Offres hors taxes"
        )
        print(f"⚠️ GPT Error: {e}")

    try:
        if not From.startswith("whatsapp:"):
            From = "whatsapp:" + From
        message = client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            body=message_texte,
            to=From
        )
        print(f"📤 Réponse envoyée : {message_texte}")
    except Exception as e:
        print(f"❌ Erreur Twilio : {e}")
        return JSONResponse(content={"error": str(e)}, status_code=400)

    return {"status": "ok"}
