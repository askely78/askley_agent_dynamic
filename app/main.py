import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from twilio.rest import Client

app = FastAPI()

# Lecture des variables d'environnement
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # Format: whatsapp:+14155238886

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.post("/whatsapp-webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...)
):
    print(f"📥 Message reçu de {From} : {Body}")

    if "hôtel" in Body.lower():
        message_texte = "🛎️ Où souhaitez-vous réserver ? Merci de préciser la ville et les dates."
    elif "restaurant" in Body.lower():
        message_texte = "🍽️ Quel type de cuisine préférez-vous et pour quelle date ?"
    elif "plat" in Body.lower():
        message_texte = "🍛 Quel plat souhaitez-vous commander ?"
    elif "artisan" in Body.lower():
        message_texte = "🧵 Quel type de produit artisanal cherchez-vous ?"
    elif "maison" in Body.lower():
        message_texte = "🏠 Dites-nous quel plat fait maison vous intéresse."
    elif "duty free" in Body.lower():
        message_texte = "🛍️ Voici nos meilleures offres duty free. Souhaitez-vous une catégorie particulière ?"
    else:
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
            "6️⃣ Offres duty free"
        )

    try:
        message = client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            body=message_texte,
            to=From
        )
        print(f"📤 Réponse : {message_texte}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return JSONResponse(content={"error": str(e)}, status_code=400)

    return {"status": "ok"}
