import json
import re
from bs4 import Tag
from geopy.geocoders import Nominatim

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    url = "https://www.santaelena.com.co/"
    page.goto(url)

    page.wait_for_load_state('networkidle')

    link_selector = '.menu-item-512'
    page.click(link_selector)

    page.wait_for_load_state('networkidle')

    links_selector2 = 'div.elementor-widget-button a'
    links = page.query_selector_all(links_selector2)

    for link in links:
        href = link.get_attribute('href')

        new_page = context.new_page()

        new_page.goto(href)

        new_page.wait_for_load_state('networkidle')

        cards = new_page.query_selector_all('div.elementor-widget-container')

        for card in cards:
            card_html = card.inner_html()

            soup = BeautifulSoup(card_html, 'lxml')

            name_list = []
            name = soup.find_all('h3', class_='elementor-heading-title')
            for i in name:
                name_list.append(i.text)
            addresses = []
            phones = []
            working_hours = []
            for element in soup.find_all('div', class_='elementor-text-editor elementor-clearfix'):
                for paragraph in element.find_all('p'):
                    if 'Dirección:' in paragraph.text:
                        address = paragraph.text
                        addresses.append(address)
                    if 'Teléfono' in paragraph.text:
                        telefono = paragraph.find_next('br').next_sibling.strip()
                        phones.append(telefono)
                for paragraph in element.find_all('h4'):
                    if 'Dirección:' in paragraph.text:
                        address = paragraph.find_next('p')
                        addresses.append(address)
                    if 'Teléfono' in paragraph.text:
                        telefono = paragraph.find_next('p')
                        telefono = telefono.text
                    else:
                        telefono = '604 325 6600 ext 4000 - 604 448 0060'
                    phones.append(telefono)
                for paragraph in element.find_all('p'):
                    if 'Horario de atención' in paragraph.text:
                        work1 = paragraph.find_next('p')
                        work2 = paragraph.find_next('br')
                        if work1:
                            next_paragraph = work1.find_next_sibling('p')
                            if next_paragraph:
                                work1_text = f"{work1.text}, {next_paragraph.text}"
                            else:
                                work1_text = work1.text
                            working_hours.append(work1_text)
                        elif work2:
                            work2_text = work2.next_sibling.strip()
                            working_hours.append(work2_text)
                for paragraph in element.find_all('h4'):
                    if 'Horario de atención' in paragraph.text:
                        work1 = paragraph.find_next('p')
                        working_hours.append(work1.text)
            addresses.pop(-2)

            links_all = []
            links_map = []

            coordinates = []

            link_elements = soup.find_all('a', class_='elementor-button-link')
            for link_element in link_elements:
                link = link_element['href']
                links_all.append(link)

            for link in links_all:
                if re.search(r'google.com/maps', link):
                    links_map.append(link)

            for url in links_map:
                geolocator = Nominatim(user_agent='my_app')
                location = geolocator.geocode(url)

                if location:
                    latitude = location.latitude
                    longitude = location.longitude


            store_data = []

            for name, address, phone, working_hours in zip(name_list, addresses, phones, working_hours):
                store = {
                    "name": name,
                    "address": address,
                    "phones": [phone],
                    "working_hours": [working_hours]
                }
                store_data.append(store)
                # Close the new page
            new_page.close()

    # Close the browser
    browser.close()
def convert_to_serializable(data):
    if isinstance(data, Tag):
        return str(data)
    elif isinstance(data, list):
        return [convert_to_serializable(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_to_serializable(value) for key, value in data.items()}
    return data

# Преобразование данных в сериализуемый формат
store_data_serializable = convert_to_serializable(store_data)

filename = "store_data.json"

# Сохранение данных в JSON-файл
with open(filename, "w", encoding='utf-8') as json_file:
    json.dump(store_data_serializable, json_file, ensure_ascii=False, indent=4)


