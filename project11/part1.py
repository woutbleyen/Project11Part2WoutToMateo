import requests
import datetime
import Sendamail

ideal_temp = float(input("Geef je ideale temperatuur (in Celsius): "))
rain_tolerance = input("Geef je regentolerantie (Zeer weinig / Minder dan 2mm / Geen voorkeur): ")
def calculate_score(avg_temp, rain_mm, ideal_temp, rain_tolerance):
    # Score op basis van temperatuur
    if abs(avg_temp - ideal_temp) <= 2:
        temp_score = 5
    elif abs(avg_temp - ideal_temp) <= 3:
        temp_score = 4
    elif abs(avg_temp - ideal_temp) <= 5:
        temp_score = 3
    elif abs(avg_temp - ideal_temp) <= 7:
        temp_score = 2
    else:
        temp_score = 1

    # Score op basis van regenval
    if rain_tolerance == "Zeer weinig" and rain_mm < 1:
        rain_score = 4
    elif rain_tolerance == "Minder dan 2mm" and rain_mm < 2:
        rain_score = 4
    else:
        rain_score = 0

    return temp_score + rain_score

def get_weather_for_destination(destinations, ideal_temp, rain_tolerance):
    destination_scores = {}

    for destination, coordinates in destinations.items():
        lat, lon = coordinates
        weather_data = get_weather_data(lat, lon)
        if weather_data:
            timeslots = weather_data.get("list")
            avg_temp, rain_mm = get_weather_for_week(timeslots)
            score = calculate_score(avg_temp, rain_mm, ideal_temp, rain_tolerance)
            destination_scores[destination] = (avg_temp, rain_mm, score)

    return destination_scores

def get_weather_for_week(timeslots):
    temperatures_first_week = []
    rain_amount_first_week = [0] * 7

    for timeslot in timeslots:
        timestamp = timeslot.get("dt")
        date = datetime.datetime.fromtimestamp(timestamp)
        if date.date() <= datetime.datetime.now().date() + datetime.timedelta(days=7):
            temperatures_first_week.append(timeslot.get("main").get("temp"))
            if "rain" in timeslot and "3h" in timeslot["rain"]:
                day_index = (date.date() - datetime.datetime.now().date()).days
                rain_amount_first_week[day_index] += timeslot["rain"]["3h"]

    avg_temp = sum(temperatures_first_week) / len(temperatures_first_week)
    avg_rain_per_day = sum(rain_amount_first_week) / 7

    return avg_temp, avg_rain_per_day

def rain_week_no_numb(avg_rain_per_day):
    if avg_rain_per_day < 1:
        rainpday = "zeer weinig"
    elif avg_rain_per_day < 2:
        rainpday = "gemiddeld"
    else:
        rainpday = "veel"
    return rainpday

def get_weather_data(lat, lon):
    response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid=bbc71d0c3567c74e05b50bdff72f635b&units=metric")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def email(content):
    mail = f"""
    Voor elk gebied vindt u in deze mail de gemiddelde temperatuur en de hoeveelheid regen die er gaat vallen 
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
    destinations = {
        "Ankara, Turkije": (39.9334, 32.8597),
        "Athene, Griekenland": (37.9838, 23.7275),
        "La Valette, Malta": (35.8989, 14.5146),
        "Sardinië, Italië": (40.1209, 9.0129),
        "Sicilië, Italië": (37.5994, 14.0154),
        "Nicosia, Cyprus": (35.1856, 33.3823),
        "Mallorca, Spanje": (39.6953, 3.0176),
        "Lagos, Portugal": (37.1028, 8.6730),
        "Mauritius": (20.3484, 57.5522),
        "Boekarest, Roemenië": (44.4268, 26.1025)
    }

    for location, coordinates in destinations.items():
        lat, lon = coordinates
        weather_data = get_weather_data(lat, lon)
        if weather_data:
            timeslots = weather_data.get("list")
            inhoud_mail += f"Weerbericht voor {location}:\n"
            avg_temp, rain_mm = get_weather_for_week(timeslots)
            score = calculate_score(avg_temp, rain_mm, ideal_temp, rain_tolerance)
            rainpday = rain_week_no_numb(rain_mm)
            inhoud_mail += f"Gemiddelde weer voor de eerste week:\n" \
                           f"Gemiddelde temperatuur: {round(avg_temp)}°C\n" \
                           f"Er word {rainpday} regenval per dag verwacht\n" \
                           f"\n"

#sorted_destinations = sorted(destination_scores.items(), key=get_score, reverse=True)

        else:
            inhoud_mail += f"Kon geen weerbericht ophalen voor {location}."

    address = input("E-mailadres: ")
    Sendamail.main(address, inhoud_mail)
    print("email send ")

if __name__ == "__main__":
    get_weather()
