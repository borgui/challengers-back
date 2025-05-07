import requests
import concurrent.futures
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from urllib.parse import urlparse
import locale

try:
    locale.setlocale(locale.LC_TIME, "French_France")  # Windows
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, "fr-FR")  # Autre format Windows
    except locale.Error:
        locale.setlocale(locale.LC_TIME, "")  # Fallback : locale système

race_ids = []

# Fonction pour scraper les données d'événements
def scrape_events():
    urls = ["https://jogging-plus.com/calendrier/courses-5-10-15-km/france/",
    "https://jogging-plus.com/calendrier/semi-marathons/france/",
    "https://jogging-plus.com/calendrier/marathons/france/",
    "https://jogging-plus.com/calendrier/trails/france/",
    "https://jogging-plus.com/calendrier/calendrier-triathlon-france/"]
    events = []
    for url in urls: 
        events.append(scrape_event(url))
    return events
   
def scrape_event(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        events = soup.find_all("tr")
        event_list = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_event, event): event for event in events}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    event_list.append(result)
        
        return event_list
    else:
        print(f"Erreur: {response.status_code}")
        return []

def process_event(event):
    optTitle = event.find("a", class_="lienorange")
    if optTitle is None:
        return
    title = optTitle.text.strip()
    details_url = event.find("a", class_="lienorange").get("href")
    race_id = get_race_id(details_url)
    if race_id in race_ids:
        return
        
    race_ids.append(race_id)
    types = event.find("em").text.strip()

    # Formatage de la date pour la base de données
    details = scrap_details(details_url)
    return {
        "race_id": race_id,
        "title": title,
        "types": types,
        **details
    }
 
def get_race_id(details_url):
    parsed_url = urlparse(details_url)
    path = parsed_url.path
    return path.rstrip('/').split('/')[-1]
 
def get_lon_lat(script_src):
    # Utilisation des expressions régulières pour extraire lat et lng
    lat_match = re.search(r'lat:\s*([-\d.]+)', script_src)
    lng_match = re.search(r'lng:\s*([-\d.]+)', script_src)

    # Vérification et extraction des valeurs
    if lat_match and lng_match:
        lat = lat_match.group(1)
        lng = lng_match.group(1)
        return [lat, lng];
    else:
        print("Latitude ou Longitude non trouvée dans l'URL.")
        
def scrap_details(url):
   if url is None or url == '':
       return {}
   response = requests.get(url)
   if response.status_code == 200:
       soup = BeautifulSoup(response.content, "html.parser")
       event = soup.find("div", class_="entry-content")
       description = event.find("em").text.strip().replace('«', '').replace('»', '')
       src_script = soup.find("script", id="stay22-script").string
       date_opt = event.find("div", id="bloc-date-fiche")
       date_string = None if date_opt == None else date_opt.text.strip()
       lat_lon = get_lon_lat(src_script)
       dates = parse_date(date_string) 
       register_link_opt = event.find("a", class_="btn_inscr_event")
       register_link = None if register_link_opt == None else register_link_opt.get("href").split("target=")[1]
       cp_city = event.find_all("div", id="bloc-info-valeur")[0].text.strip().splt(" - ")
       department_region = event.find_all("div", id="bloc-info-valeur")[1].text.strip().splt(" / ")


       return {
          "description": description,
          "lat": lat_lon[0],
          "lon": lat_lon[1],
          "postal_code": cp_city[0],
          "city": cp_city[1],
          "department": department_region[1],
          "register_link": register_link,
          **dates
       }
       
   return {}
       

def parse_date(date_str):
    date1 = None
    date2 = None
    
    if date_str is None or "DATE A VENIR" in date_str or "Non connue" in date_str:
       return { 
            "startDate": date1,
            "endDate": date2
       }
    date_str = date_str.replace("juil.", "juillet")
    if " au " in date_str:
        # Diviser la chaîne en deux parties
        date_parts = date_str.split(" au ")

        # Supposons que la deuxième partie contient toujours le mois et l'année
        date2 = datetime.strptime(date_parts[1], "%d %B %Y")
         
        # Vérifier si la première partie ne contient que le jour
        if len(date_parts[0].split()) == 1:  # Si seul le jour est donné
            date_parts[0] += f" {date2.strftime('%B %Y')}"  # Ajouter mois et année
        elif len(date_parts[0].split()) == 2:  # Si seul le jour et mois est donné
            date_parts[0] += f" {date2.strftime('%Y')}"  # Ajouter année

        # Convertir les deux dates en datetime
        date1 = datetime.strptime(date_parts[0], "%d %B %Y").isoformat()
        date2 = date2.isoformat()
    else:
        date_format = "%A %d %B %Y"
        # Convertir la chaîne en un objet datetime
        date1 = datetime.strptime(date_str, date_format).isoformat()

    return { 
            "startDate": date1,
            "endDate": date2
    }
    
# Fonction pour écrire les données dans un fichier json
def write_to_json(event_list):
    # Serializing json
    json_object = json.dumps(event_list, indent=4, ensure_ascii=False)
 
    # Writing to sample.json
    with open("events.json", "w", encoding="utf-8") as outfile:
        outfile.write(json_object)

# Scraper les événements
events = scrape_events()
# Écrire les événements dans un fichier Excel
if events:
    write_to_json(events)
    print("Scraping et insertion dans le fichier Excel terminés.")
else:
    print("Aucun événement à insérer.")
