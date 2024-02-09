import re
import json

import requests
from bs4 import BeautifulSoup

cookies = {

}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://dentalia.com',
    'Referer': 'https://dentalia.com/clinica/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "YaBrowser";v="24.1", "Yowser";v="2.5"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    'nocache': '1707385091',
}

data = {
    'action': 'jet_engine_ajax',
    'handler': 'get_listing',
    'page_settings[post_id]': '5883',
    'page_settings[queried_id]': '344706|WP_Post',
    'page_settings[element_id]': 'c1b6043',
    'page_settings[page]': '1',
    'listing_type': 'elementor',
    'isEditMode': 'false',
}

response = requests.post('https://dentalia.com/', params=params, cookies=cookies, headers=headers, data=data)
data = json.loads(response.text)
html_content = data['data']['html']
soup = BeautifulSoup(html_content, 'lxml')
shop_list = []
printed_coordinates = []
result_shop = []
# Теперь вы можете работать с объектом BeautifulSoup для анализа HTML
# Например, вы можете найти определенные элементы по их тегам или атрибутам
div_elements = soup.find_all('section', attrs={"data-id": "a02bd13"})
for el in div_elements:
    name = el.find('h3', class_='elementor-heading-title elementor-size-default').text
    address = el.find('div', class_='jet-listing-dynamic-field__content').text
    tel = el.find('div', attrs={"data-id": "cb84d19"}).text
    if tel is not None:
        phone_numbers = re.sub(r'Teléfono\(s\):\s*', '', tel)
        numbers = re.sub(r'[\n\r]', '', phone_numbers)
        # Извлечь номера телефонов при помощи регулярных выражений
        numbers = re.findall(r'\(\d{2,3}\)[\d\s-]+', numbers)
        # Сформировать выходной словарь
        phones = {'phones': numbers}
    working_hours = el.find('div', attrs={"data-id": "9e2c33b"}).text
    working_hours = re.sub(r'Horario:\s*', '', working_hours)
    working_hours = [line.strip() for line in working_hours.split('\n') if line.strip()]
    # поиск координат
    tags = el.find_all("div", attrs={"data-id": "a6c6867"})
    for i in tags:
        a_tags = i.find_all('a', class_='elementor-button-link elementor-button elementor-size-md')
        href_list = [a['href'] for a in a_tags]
        for href in href_list:
            match = re.search(r'@([-\d.]+),([-\d.]+)', href)

            if match:
                latitude = float(match.group(1))
                longitude = float(match.group(2))

                latlon = [abs(latitude), abs(longitude)]

            else:
                latlon = []
    latlon_string = ', '.join(map(str, latlon))
    phones_string = ', '.join(phones['phones'])
    working_hours_string = ', '.join(working_hours)

    result_shop.append({
        'name': name,
        'address': address,
        'latlon': [latlon_string],
        'phones': [phones_string],
        'working_hours': [working_hours_string]
    })

with open('data.json', 'w', encoding='utf-8') as file:
    json.dump(result_shop, file, ensure_ascii=False, indent=4)
