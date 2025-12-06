import os
import requests


# ✅ Clé API WeatherAPI (mets ta vraie clé ici ou dans une variable d’environnement)
API_KEY = os.getenv("WEATHER_API_KEY", "b9e0e331575e4d659aa125326252310")
BASE_URL = "http://api.weatherapi.com/v1/current.json"


def get_weather_icon(condition: str) -> str:
    """Retourne une icône météo selon la condition"""
    condition = condition.lower()
    if "pluie" in condition:
        return "🌧️"
    elif "nuage" in condition:
        return "☁️"
    elif "soleil" in condition or "clair" in condition:
        return "☀️"
    elif "neige" in condition:
        return "❄️"
    elif "orage" in condition:
        return "⛈️"
    else:
        return "🌡️"


def get_weather(city: str) -> str:
    """Récupère la météo actuelle d'une ville avec gestion des erreurs"""
    params = {
        "key": API_KEY,
        "q": city,
        "lang": "fr"
    }

    try:
        # 🔹 Requête à l’API avec timeout
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()  # Lève une erreur si HTTP != 200
        data = response.json()

        # Vérifie si l’API renvoie une erreur (ex: ville inconnue)
        if "error" in data:
            return f"⚠️ Erreur : {data['error']['message']}"

        # 🔹 Extraction des données utiles
        ville = data["location"]["name"]
        pays = data["location"]["country"]
        temperature = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        heure = data["location"]["localtime"]
        humidite = data["current"]["humidity"]
        vent = data["current"]["wind_kph"]

        icon = get_weather_icon(condition)

        # 🔹 Formatage de la réponse
        return (
            f"{icon} À {ville} ({pays}) :\n"
            f"🌡️ Température : {temperature}°C\n"
            f"☁️ Condition : {condition.lower()}\n"
            f"💨 Vent : {vent} km/h\n"
            f"💧 Humidité : {humidite}%\n"
            f"🕓 Heure locale : {heure}"
        )

    # 🔹 Gestion complète des erreurs possibles
    except requests.exceptions.Timeout:
        return "⏳ Le serveur met trop de temps à répondre. Réessaie plus tard."
    except requests.exceptions.ConnectionError:
        return "🚫 Impossible de se connecter à Internet ou à l'API."
    except requests.exceptions.RequestException as e:
        return f"❌ Erreur de requête : {e}"
    except KeyError:
        return "⚠️ Données météo incomplètes ou inattendues."


def chatbot():
    """Boucle principale du chatbot"""
    print("=== 🤖 Chatbot Météo (WeatherAPI) ===")
    print("Tape 'quit' pour arrêter.\n")

    while True:
        user_input = input("👤 Vous : ").strip()
        if user_input.lower() in ["quit", "exit", "stop"]:
            print("🤖 Chatbot : À bientôt ! 👋")
            break
        elif not user_input:
            print("🤖 Chatbot : Merci d’entrer une ville valide !")
        else:
            print("🤖 Chatbot :")
            print(get_weather(user_input))
            print()


if __name__ == "__main__":
    chatbot()

