from bs4 import BeautifulSoup


def get_destinations(destinations_section_title):
    from app import app  # Avoid circular import

    # Get Airlines and destinations table
    destinations_table = destinations_section_title.find_next('table', class_="wikitable sortable")

    destination_dict = {
        "general": {},
        "seasonal": {},
        "charter": {},
        "seasonal charter": {}
    }

    for row in destinations_table.find_all('tr')[1:]:  # Skip header row

        # Find the second column
        second_column = row.find_all('td')[1]

        if second_column.find_all('b'):  # Case <b> in the cell, handle destination differently
            # Parse to str and split by <br/>, the first part is the general destinations
            parts_str = str(second_column).split("<br/>")

            # Extract general destinations, if <b> in parts_str[0], illustrate that the airlines doesn't have general flights destinations
            if '<b>' not in parts_str[0]:
                general_destinations_str = parts_str[0]
                general_destinations_soup = BeautifulSoup(general_destinations_str, "html.parser")
                destination_dict = add_destinations_to_dict(destination_dict, general_destinations_soup, 'general')

                # Remove general part
                parts_str = parts_str[1:]

            # Handle special destinations (seasonal / charter / seasonal charter)
            for part_str in parts_str:
                part_soup = BeautifulSoup(part_str, "html.parser")

                # Get the special destination type (in a <b> tag)
                b_tag = part_soup.find('b')
                if b_tag:
                    special_type = b_tag.string.strip()[:-1].lower() if ':' in b_tag.string.strip() else b_tag.string.strip().lower()

                    # Init the special dict in the destinations dict
                    if special_type not in destination_dict:
                        # destination_dict[special_type] = {}
                        app.logger.warning('Can not identified special type:', special_type)

                    destination_dict = add_destinations_to_dict(destination_dict, part_soup, special_type)

        else:  # Case no <br/> in the cell, extract destination info directly
            destination_dict = add_destinations_to_dict(destination_dict, second_column, 'general')

    return destination_dict


def add_destinations_to_dict(destination_dict, soup, dest_type):

    for link in soup.find_all('a'):
        href = link.get('href')

        if href.startswith('/wiki/'):  # Filter references link
            city = link.text

            # Check if the destination already exists in higher priority types
            if city in destination_dict['general'] and dest_type != 'general':
                continue
            if city in destination_dict['seasonal'] and dest_type in ['charter', 'seasonal charter']:
                continue
            if city in destination_dict['charter'] and dest_type == 'seasonal charter':
                continue

            # Add the destination to the corresponding type
            destination_dict[dest_type][city] = href

            # Remove the link from lower priority types if necessary
            for lower_type in ['seasonal charter', 'charter', 'seasonal']:
                if lower_type != dest_type and city in destination_dict[lower_type]:
                    del destination_dict[lower_type][city]

    return destination_dict


def get_wikidata_id(html):

    # Find "Wikidata Item" list item in sidebar
    wikidata_li = html.find(id="t-wikibase")

    # Case the article itself hasn't connected to Wikidata
    if wikidata_li is None:
        return None

    # Get url of "Wikidata Item"
    wikidata_a = wikidata_li.find_all('a')[0]
    url = wikidata_a.get('href')

    # Return Wikidata ID
    return url[url.rfind('/') + 1:]
