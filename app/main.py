import os
from typing import Dict
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from twilio.rest import Client

app = FastAPI()

# Variables d'environnement correctement nommées
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_WHATSAPP_FROM")  # Format : whatsapp:+14155238886

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Mémoire des utilisateurs (par session)
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

    if From not in session_memory:
        session_memory[From] = {}

    # Logique des intentions
    if "hôtel" in body_lower:
        session_memory[From]["last_intent"] = "hotel"
        message_texte = "🏨 Pour quelle ville et quelles dates souhaitez-vous réserver un hôtel ?"
    elif "restaurant" in body_lower:
        session_memory[From]["last_intent"] = "restaurant"
        message_texte = "🍽️ Dans quelle ville souhaitez-vous réserver un restaurant ?"
    elif "plat" in body_lower or "commander" in body_lower:
        session_memory[From]["last_intent"] = "plat"
        message_texte = "🥘 Quels plats souhaitez-vous commander ? (couscous, tajine, tanjia, etc.)"
    elif "artisan" in body_lower:
        session_memory[From]["last_intent"] = "artisan"
        message_texte = "🧵 Quel type de produits artisanaux cherchez-vous ?"
    elif "maison" in body_lower:
        session_memory[From]["last_intent"] = "maison"
        message_texte = "🏡 Découvrez nos plats faits maison. Qu’est-ce qui vous ferait plaisir ?"
    elif "duty free" in body_lower or "offre" in body_lower:
        session_memory[From]["last_intent"] = "duty"
        message_texte = "🛍️ Voici nos offres duty free. Quelle est votre destination ?"
    elif body_lower in ["1", "2", "3", "4", "5", "6"]:
        message_texte = "✳️ Merci pour votre choix. Veuillez préciser les détails."
    elif session_memory[From].get("last_intent") == "hotel":
        session_memory[From]["ville"] = Body
        message_texte = f"📅 Merci ! Nous allons chercher un hôtel à {Body}. Souhaitez-vous ajouter une date ?"
    elif session_memory[From].get("last_intent") == "restaurant":
        session_memory[From]["ville"] = Body
        message_texte = f"🍽️ Très bien ! Nous cherchons un restaurant à {Body}."
    elif session_memory[From].get("last_intent") == "plat":
        session_memory[From]["plat"] = Body
        message_texte = f"✅ Noté ! Plat commandé : {Body}."
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

    # Vérification du format du numéro d'expéditeur Twilio
    if not TWILIO_PHONE_NUMBER or not TWILIO_PHONE_NUMBER.startswith("whatsapp:"):
        error_msg = "Numéro Twilio mal configuré. Vérifiez TWILIO_WHATSAPP_FROM."
        print(f"❌ Erreur : {error_msg}")
        return JSONResponse(content={"error": error_msg}, status_code=400)

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
