import Sendamail
import requests
import datetime

print(" even geduld ")
def calculate_score(avg_temp, snow_cm):
    if avg_temp < 0:
        score = 5
    elif 0 <= avg_temp < 5:
        score = 4
    elif 5 <= avg_temp < 10:
        score = 3
    else:
        score = 1
    # Voeg +1 toe aan de score als er meer dan 5 cm sneeuw voorspeld wordt
    if snow_cm > 5:
        score += 1
        # Zorg ervoor dat de score niet hoger wordt dan 5
        if score > 5:
            score = 5

    return score

def get_weather_for_week(timeslots):
    temperatures_first_week = []
    snow_amount_first_week = 0

    # Groepeer timeslots per week en sla de weersgegevens van de eerste week op
    for timeslot in timeslots:
        timestamp = timeslot.get("dt")
        date = datetime.datetime.fromtimestamp(timestamp).date()
        if date.isocalendar()[1] == datetime.datetime.now().isocalendar()[1]:
            temperatures_first_week.append(timeslot.get("main").get("temp"))
            if "snow" in timeslot:
                snow_amount_first_week += timeslot["snow"]["3h"] if "3h" in timeslot["snow"] else 0

    # Omzetten van mm naar cm en afronden tot 2 decimalen
    snow_cm = round(snow_amount_first_week / 10, 2)
    # De gemiddelde temperatuur per week
    avg_temp = sum(temperatures_first_week) / len(temperatures_first_week)

    return snow_cm, avg_temp

def get_weather_data(lat, lon):
    response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?"
                            f"lat={lat}&lon={lon}&appid=bbc71d0c3567c74e05b50bdff72f635b&units=metric")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def email(content):
    mail = f"""
    Voor elk gebied vindt u in deze mail de gemiddelde temperatuur en de hoeveelheid sneeuw die er gaat vallen 
    van de komende week.
    Er staat ook een score op /5: dit houdt in hoe hoger de score, 
    hoe beter het is om daar op vakantie te gaan.

    {content}
    """
    address = input("mailadres: ")

    Sendamail.main(address, mail)
    print("Mail sent")

def get_weather():
    inhoud_mail = ""
    locations = {
        "Les Trois Vallées": (45.3356, 6.5890),
        "Sölden": (46.9701, 11.0078),
        "Chamonix Mont Blanc": (45.9237, 6.8694),
        "Val di Fassa": (46.4265, 11.7684),
        "Salzburger Sportwelt": (47.3642, 13.4639),
        "Alpenarena Films-Laax-Falera": (46.8315, 9.2663),
        "Kitzsteinhorn Kaprun": (47.1824, 12.6912),
        "Ski Altberg": (47.43346, 8.42053),
        "Espace Killy": (45.4481, 6.9806),
        "Špindlerův Mlýn": (50.7296, 15.6075)
    }

    for location, coordinates in locations.items():
        lat, lon = coordinates
        weather_data = get_weather_data(lat, lon)
        if weather_data:
            timeslots = weather_data.get("list")
            inhoud_mail += f"Weerbericht voor {location}:\n"
            avg_temp, snow_cm = get_weather_for_week(timeslots)
            score = calculate_score(avg_temp, snow_cm)
            inhoud_mail += f"Gemiddelde weer voor de eerste week:\n" \
                           f"Gemiddelde temperatuur: {round(avg_temp)}°C\n" \
                           f"Totale hoeveelheid sneeuw: {round(snow_cm)} cm\n" \
                           f"Score: {score}/5\n\n"
        else:
            inhoud_mail += f"Kon geen weerbericht ophalen voor {location}."

        # Verzend e-mail met weerinformatie
    address = input("E-mailadres: ")
    Sendamail.main(address, inhoud_mail)


if __name__ == "__main__":
    get_weather()