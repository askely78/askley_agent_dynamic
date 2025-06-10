import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from twilio.rest import Client

app = FastAPI()

# Variables d'environnement
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # Format : whatsapp:+14155238886

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.get("/")
def read_root():
    return {"message": "Askley backend is live ✅"}

@app.post("/whatsapp-webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...)
):
    print(f"📥 Message reçu de {From} : {Body}")

    # Mise en minuscule pour simplifier les comparaisons
    body_lower = Body.lower()

    # Logique simple d'intentions par mots-clés
    if "hôtel" in body_lower:
        message_texte = "🏨 Très bien ! Pour quelle ville et quelles dates souhaitez-vous réserver un hôtel ?"
    elif "restaurant" in body_lower:
        message_texte = "🍽️ Avec plaisir ! Dans quelle ville souhaitez-vous réserver un restaurant ?"
    elif "plat" in body_lower or "commander" in body_lower:
        message_texte = "🥘 Quels plats souhaitez-vous commander ? Nous avons couscous, tajine, tanjia, etc."
    elif "artisan" in body_lower:
        message_texte = "🧵 Nous proposons des produits artisanaux marocains authentiques. Quel type cherchez-vous ?"
    elif "maison" in body_lower:
        message_texte = "🏡 Découvrez nos plats faits maison. Dites-moi ce qui vous fait envie !"
    elif "duty free" in body_lower or "offre" in body_lower:
        message_texte = "🛍️ Voici nos offres spéciales disponibles dans les duty free. Vous avez une destination en tête ?"
    elif body_lower in ["1", "2", "3", "4", "5", "6"]:
        message_texte = "✳️ Merci pour votre choix, nous allons continuer. Veuillez préciser les détails."
    else:
        message_texte = (
            "👋 Bienvenue chez Askley !\n"
            "1️⃣ Réserver un hôtel\n"
            "2️⃣ Réserver un restaurant\n"
            "3️⃣ Commander un plat\n"
            "4️⃣ Produits artisanaux\n"
            "5️⃣ Plats faits maison\n"
            "6️⃣ Offres hors taxes"
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
