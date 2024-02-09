import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

all_data = []
formatted_data = []  # Создаем новый список для отформатированных данных

def parse_store_data(card_html):
    soup = BeautifulSoup(card_html, 'html.parser')
    data = {
        "name": "",
        "address": "",
        "latlon": [],
        "phones": [],
        "working_hours": []
    }

    # Extract and save store names
    names = [element.text.strip() for element in soup.find_all('h3', class_='elementor-size-default') if
             element.text.strip()]

    # Extract and save addresses, phones, and working hours
    addresses = []
    phones = []
    working_hours = []
    for element in soup.find_all('div', class_='elementor-text-editor'):
        for paragraph in element.find_all('p'):
            if 'Dirección:' in paragraph.text:
                address = paragraph.text.split(':', 1)[1].strip()
                if address:
                    addresses.append(address)
            elif 'Teléfono:' in paragraph.text:
                phone_list = [phone.strip() for phone in paragraph.text.split(':', 1)[1].split(',')]
                phones.extend(phone_list)
            elif 'Horario de atención:' in paragraph.text:
                hours_list = [line.strip() for line in paragraph.text.split(':', 1)[1].split('\n') if line.strip()]
                working_hours.extend(hours_list)

    # Remove empty elements from lists
    addresses = [address for address in addresses if address]
    phones = [phone for phone in phones if phone]
    working_hours = [hours for hours in working_hours if hours]

    # Check if at least one field is not empty
    if names:
        data["name"] = names
        data["address"] = addresses
        data["phones"] = phones
        data["working_hours"] = working_hours
        data["latlon"] = [6.1991563, -75.574123]
        return data
    else:
        return None  # Return None if no names were found


with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()

    url = "https://www.santaelena.com.co/"
    page.goto(url)

    # Ждем загрузки контента
    page.wait_for_load_state('networkidle')

    # Находим ссылку и кликаем на нее
    link_selector = '.menu-item-512'
    page.click(link_selector)

    # Ждем загрузки контента
    page.wait_for_load_state('networkidle')

    # Находим все ссылки по указанному селектору
    links_selector2 = 'div.elementor-widget-button a'
    links = page.query_selector_all(links_selector2)

    for link in links:
        href = link.get_attribute('href')

        # Открываем новую страницу
        new_page = context.new_page()

        # Переходим по ссылке
        new_page.goto(href)

        # Ждем загрузки контента
        new_page.wait_for_load_state('networkidle')

        # Находим нужные элементы на странице
        cards = new_page.query_selector_all('div.elementor-widget-container')

        for card in cards:
            card_html = card.inner_html()
            data = parse_store_data(card_html)
            if data is not None:  # Check if data is not None before trying to access its keys
                formatted_data.append({
                    "name": data["name"],
                    "address": data["address"],
                    "latlon": data["latlon"],
                    "phones": data["phones"],
                    "working_hours": data["working_hours"]
                })

    # Закрываем новую страницу
        new_page.close()

    # Закрываем браузер
    browser.close()

# Записываем данные в файл JSON
with open('santa_elena.json', 'w', encoding='utf-8') as json_file:
    json.dump(formatted_data, json_file, ensure_ascii=False, indent=4)
