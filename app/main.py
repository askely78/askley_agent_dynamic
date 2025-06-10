
import os
from typing import Dict
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from twilio.rest import Client

app = FastAPI()

# Variables d'environnement
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_WHATSAPP_FROM")  # Format : whatsapp:+14155238886

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Mémoire temporaire des sessions utilisateur
session_memory: Dict[str, Dict[str, str]] = {}

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

    body_lower = Body.lower()
    message_texte = ""

    # Initialiser mémoire si nouveau numéro
    if From not in session_memory:
        session_memory[From] = {}

    # Intentions dynamiques
    if "hôtel" in body_lower:
        session_memory[From]["last_intent"] = "hotel"
        message_texte = "🏨 Très bien ! Pour quelle ville et quelles dates souhaitez-vous réserver un hôtel ?"
    elif "restaurant" in body_lower:
        session_memory[From]["last_intent"] = "restaurant"
        message_texte = "🍽️ Avec plaisir ! Dans quelle ville souhaitez-vous réserver un restaurant ?"
    elif "plat" in body_lower or "commander" in body_lower:
        session_memory[From]["last_intent"] = "plat"
        message_texte = "🥘 Quels plats souhaitez-vous commander ? Nous avons couscous, tajine, tanjia, etc."
    elif "artisan" in body_lower:
        session_memory[From]["last_intent"] = "artisan"
        message_texte = "🧵 Nous proposons des produits artisanaux marocains authentiques. Quel type cherchez-vous ?"
    elif "maison" in body_lower:
        session_memory[From]["last_intent"] = "maison"
        message_texte = "🏡 Découvrez nos plats faits maison. Dites-moi ce qui vous fait envie !"
    elif "duty free" in body_lower or "offre" in body_lower:
        session_memory[From]["last_intent"] = "duty"
        message_texte = "🛍️ Voici nos offres spéciales disponibles dans les duty free. Vous avez une destination en tête ?"
    elif body_lower in ["1", "2", "3", "4", "5", "6"]:
        message_texte = "✳️ Merci pour votre choix. Veuillez maintenant préciser les détails."
    elif session_memory[From].get("last_intent") == "hotel":
        session_memory[From]["ville"] = Body
        message_texte = f"📅 Merci ! Nous allons chercher un hôtel à {Body}. Souhaitez-vous ajouter une date ?"
    elif session_memory[From].get("last_intent") == "restaurant":
        session_memory[From]["ville"] = Body
        message_texte = f"🍽️ Très bien ! Nous cherchons un restaurant à {Body}."
    elif session_memory[From].get("last_intent") == "plat":
        session_memory[From]["plat"] = Body
        message_texte = f"✅ Nous avons bien noté votre choix de plat : {Body}."
    elif session_memory[From].get("last_intent") == "artisan":
        session_memory[From]["produit"] = Body
        message_texte = f"🎨 Très bon choix ! Nous allons vous proposer des {Body} artisanaux."
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
        if not From.startswith("whatsapp:"):
            From = "whatsapp:" + From
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
