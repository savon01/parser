import json

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
# Создайте список для объектов с данными
data_list = []

# Инициализация Playwright
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page()

    url = "https://www.santaelena.com.co/"
    page.goto(url)

    # Ждем загрузки контента
    page.wait_for_load_state('networkidle')

    # Находим ссылку и кликаем на нее
    link_selector = 'li.menu-item-512'
    link = page.query_selector(link_selector)
    link.click()

    # Ждем загрузки контента
    page.wait_for_load_state('networkidle')

    # Находим все ссылки по указанному селектору
    links_selector2 = 'div.elementor-widget-button a'
    links = page.query_selector_all(links_selector2)

    all_data = []  # Список для хранения данных со всех страниц

    for link in links:
        href = link.get_attribute('href')

        # Открываем новую страницу
        new_page = browser.new_page()

        # Переходим по ссылке
        new_page.goto(href)

        # Ждем загрузки контента
        new_page.wait_for_load_state('networkidle')

        # Находим нужные элементы на странице
        cards = new_page.query_selector_all('div.elementor-widget-container')

        for card in cards:
            card_html = card.inner_html()
            soup = BeautifulSoup(card_html, 'html.parser')
            element = soup.find_all('h3', class_='elementor-heading-title')

            # for name in element:
            #     if name is not None:
            #         print(name.text)
            divs = soup.find_all('div', class_='elementor-text-editor elementor-clearfix')

            # Iterate over each div and extract the data
            for div in divs:
                address = None
                for p in div.find_all('p'):
                    # Check if the paragraph starts with "Dirección:"
                    if p.strong and p.strong.text.strip() == "Dirección":
                        # Extract the text after "Dirección:"
                        address = p.text.split(':', 1)[1].strip()
                        break  # No need to continue if we found the address

                # Print the address
                if address:
                    print(f"Dirección: {address}")
                else:
                    print("Dirección no encontrada.")
        # Закрываем новую страницу
        new_page.close()

    # Закрываем браузер
    browser.close()

with open('senta_elena.json', 'w', encoding='utf-8') as json_file:
    json.dump(data_list, json_file, ensure_ascii=False, indent=4)



