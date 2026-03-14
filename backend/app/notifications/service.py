async def sms_sos(telephone: str, nom: str, latitude: float, longitude: float) -> bool:
    message = (
        f"ALERTE SAFETRACK\n"
        f"{nom} est en danger!\n"
        f"Position: {latitude},{longitude}\n"
        f"Maps: https://maps.google.com/?q={latitude},{longitude}"
    )
    try:
        import africastalking
        from app.config import settings
        africastalking.initialize(username=settings.AT_USERNAME, api_key=settings.AT_API_KEY)
        sms = africastalking.SMS
        sms.send(message, [telephone])
        return True
    except Exception as e:
        print(f"SMS non envoye: {e}")
        return False


async def sms_arrivee_manquee(telephone: str, nom: str, lieu: str, retard: int) -> bool:
    message = (
        f"SAFETRACK\n"
        f"{nom} n'est pas arrive(e) a {lieu}\n"
        f"Retard: {retard} minutes"
    )
    try:
        import africastalking
        from app.config import settings
        africastalking.initialize(username=settings.AT_USERNAME, api_key=settings.AT_API_KEY)
        sms = africastalking.SMS
        sms.send(message, [telephone])
        return True
    except Exception as e:
        print(f"SMS non envoye: {e}")
        return False