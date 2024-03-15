import bs4
import requests
from bs4 import BeautifulSoup

from utils import make_response
from services import soup_service, database_service


def handle_original_url(url):
    response = requests.get(url)

    if response.status_code != 200:
        return make_response(response.status_code, "Invalid input URL")

    # Get Wikipedia page data
    response_data = response.text

    # Parse with Beautifulsoup
    soup = BeautifulSoup(response_data, 'html.parser')

    # Get "Airlines and destinations" section title
    destinations_section_title = soup.find(id="Airlines_and_destinations")

    # Validate "Airlines and destinations" table exists
    if type(destinations_section_title) is not bs4.element.Tag:
        return make_response(403, "Cannot find Airlines and destinations section")

    # Get destinations
    destination_dict = soup_service.get_destinations(destinations_section_title)

    # Get the country belongs to
    self_country = get_self_country(soup)

    # Get airport objects
    destinations, statistics = database_service.get_airports(destination_dict, self_country)

    return make_response(200, "Success", {
        "statistics": statistics,
        "destinations": destinations
    })


def handle_destination_url(path):
    url = "https://en.wikipedia.org" + path

    response = requests.get(url)

    # If Wikipedia doesn't have the airport article, cannot find information
    if response.status_code != 200:
        return None

    # Get Wikipedia page data
    response_data = response.text

    # Parse with Beautifulsoup
    soup = BeautifulSoup(response_data, 'html.parser')

    wikidata_id = soup_service.get_wikidata_id(soup)

    # If Wikidata doesn't have the item, cannot find information
    if wikidata_id is None:
        return None

    # Get wikidata entity json
    entity_data = get_wikidata_json(wikidata_id)

    # Get json info
    name = safe_get_json_data(entity_data, ['labels', 'en', 'value'])

    iata = safe_get_json_data(entity_data, ['claims', 'P238', 0, 'mainsnak', 'datavalue', 'value'])  # P238: IATA
    icao = safe_get_json_data(entity_data, ['claims', 'P239', 0, 'mainsnak', 'datavalue', 'value'])  # P239: ICAO

    coord = safe_get_json_data(entity_data, ['claims', 'P625', 0])  # P625: Coordinate
    lat = safe_get_json_data(coord, ['mainsnak', 'datavalue', 'value', 'latitude'])
    long = safe_get_json_data(coord, ['mainsnak', 'datavalue', 'value', 'longitude'])

    country_id = safe_get_json_data(entity_data, ['claims', 'P17', 0, 'mainsnak', 'datavalue', 'value', 'id'])  # P17: Country
    country = find_country(country_id) if country_id is not None else None

    return {
        "wikidata": wikidata_id,
        "name": name,
        "iata": iata,
        "icao": icao,
        "lat": lat,
        "long": long,
        "country": country
    }


def find_country(wikidata_id):
    country = database_service.get_country(wikidata_id)

    # If country in database, return the result
    if country:
        return country

    # Get wikidata entity json
    entity_data = get_wikidata_json(wikidata_id)
    country = safe_get_json_data(entity_data, ['labels', 'en', 'value'])

    # Save to database
    database_service.save_country(wikidata_id, country)

    return country


def get_wikidata_json(wikidata_id):
    # Concat the wikidata url
    wikidata_url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"

    wikidata_response = requests.get(wikidata_url)

    # Other status codes are unlikely to occur
    if wikidata_response.status_code != 200:
        return None

    # Get country info from Wikidata JSON
    wikidata_data = wikidata_response.json()
    return list(wikidata_data['entities'].values())[0]


def get_self_country(soup):
    wikidata_id = soup_service.get_wikidata_id(soup)

    # If Wikidata doesn't have the item, cannot find information
    if wikidata_id is None:
        return None

    # Get wikidata entity json
    entity_data = get_wikidata_json(wikidata_id)

    country_id = safe_get_json_data(entity_data, ['claims', 'P17', 0, 'mainsnak', 'datavalue', 'value', 'id'])  # P17: Country
    return find_country(country_id) if country_id is not None else None


def safe_get_json_data(data, keys):
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError):
            return None
    return data
