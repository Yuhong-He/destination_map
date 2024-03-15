from models import AirportModel, AirportSchema, CountryModel
from exts import db
from urllib.parse import unquote


def get_airports(dest_dict, self_country):
    from services import rest_service  # Avoid circular import

    destinations = {}
    count = {
        "total": 0,
        "by_region": {
            "domestic": 0,
            "international": 0
        },
        "by_type": {}
    }

    for dest_type in dest_dict:

        # Init
        destinations[dest_type] = []
        count['by_type'][dest_type] = 0

        for city in dest_dict[dest_type]:

            count['total'] += 1
            count['by_type'][dest_type] += 1

            # Extract airport name from Wikipedia url
            encoded_airport_name = dest_dict[dest_type][city][len('/wiki/'):].replace('_', ' ')

            # Decode airport name from URL
            airport_name = unquote(encoded_airport_name)

            # Get data from database
            airport = AirportModel.query.get(airport_name)

            if airport is not None:
                # Convert to json and add to result list
                airport_schema = AirportSchema()
                destinations[dest_type].append(airport_schema.dump(airport))

                # Count domestic / international destinations
                if airport.country == self_country:
                    count['by_region']['domestic'] += 1
                else:
                    count['by_region']['international'] += 1

            else:
                # Get the airport info from Wikidata
                path = dest_dict[dest_type][city]
                result = rest_service.handle_destination_url(path)

                if result is not None:
                    # Case Wikidata has the destination airport item
                    new_airport = AirportModel(alias=airport_name, wikidata=result['wikidata'],
                                               name=result['name'], short=city,
                                               iata=result['iata'], icao=result['icao'],
                                               lat=result['lat'], long=result['long'],
                                               country=result['country'])

                    # Save to database
                    db.session.add(new_airport)
                    db.session.commit()

                    # Add to result list
                    airport_schema = AirportSchema()
                    destinations[dest_type].append(airport_schema.dump(new_airport))

                    # Count domestic / international destinations
                    if result['country'] is not None:
                        if result['country'] == self_country:
                            count['by_region']['domestic'] += 1
                        else:
                            count['by_region']['international'] += 1

                else:
                    # Case Wikipedia doesn't have the destination airport article, or Wikidata doesn't have the item
                    destinations[dest_type].append({'name': airport_name, 'wikidata': None})

    return destinations, count


def get_country(country_id):
    # Get data from database
    country = CountryModel.query.get(country_id)

    return country.name if country else None


def save_country(country_id, country_name):
    country = CountryModel(wikidata=country_id, name=country_name)

    db.session.add(country)
    db.session.commit()
