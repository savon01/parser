import json
import re

from playwright.sync_api import sync_playwright

city = {'omsk':'Омск','achinsk':'Ачинск', 'berdsk':'Бердск', 'krsk':'Красноярск', 'nsk':'новосибирск', 'tomsk':'Томск'}

# Создайте список для объектов с данными
data_list = []

# Инициализация Playwright
with sync_playwright() as playwright:

    for key, value in city.items():
        browser = playwright.chromium.launch()
        page = browser.new_page()
        url = "https://{}.yapdomik.ru/about".format(key)
        # Откройте страницу
        page.goto(url)

        # Подождите, пока контент полностью не загрузится
        page.wait_for_load_state('networkidle')

        # Получите ссылку на номер телефона
        phone_link = page.query_selector('.link.link--black.link--underline')
        phone_href = phone_link.get_attribute('href')
        digits = re.findall(r'\d', phone_href)
        formatted_number = "+{}({}{}{}){}{}-{}{}-{}{}".format(*digits)

        # Найдите все элементы <li> с геоданными
        elements = page.query_selector_all('li[data-latitude][data-longitude]')

        # Переберите все элементы и получите геоданные и график работы
        for element in elements:
            # Получите геоданные из атрибутов data-latitude и data-longitude
            latitude = element.get_attribute('data-latitude')
            longitude = element.get_attribute('data-longitude')

            # Найдите ссылку внутри элемента <li>
            link = element.query_selector('span.link')

            # Получите текст ссылки
            link_text = link.inner_text()

            link_text = value + ',' + link_text
            # Создайте объект с данными
            data = {
                "name": "Японский Домик",
                "address": link_text,
                "latlon": ["{},{}".format(latitude, longitude)],
                "phones": [formatted_number],
                "working_hours": []  # Изначально график работы пустой
            }

            # Кликните на ссылку для получения графика работы
            link.click()

            # Дождитесь, пока ссылка станет активной
            page.wait_for_selector('li.active')

            # Проверьте наличие элемента с данными на карте
            data_element = page.query_selector('.ymaps-2-1-79-balloon__content')

            if data_element:
                # Распарсите данные для получения графика работы и времени
                work_time_element = data_element.query_selector('.work-time')
                work_days = work_time_element.query_selector('div:nth-child(1)').inner_text()
                work_hours = work_time_element.query_selector('div:nth-child(2)').inner_text()

                # Обновите объект с данными
                data["working_hours"] = ["{} {}".format(work_days, work_hours)]

                # Закройте окно с данными на карте
                page.click('.ymaps-2-1-79-balloon__close-button')

            # Добавьте объект в список
            data_list.append(data)

        # Закройте браузер после завершения
        browser.close()

# Создайте JSON-файл из списка данных
with open('yapdomik.json', 'w', encoding='utf-8') as json_file:
    json.dump(data_list, json_file, ensure_ascii=False, indent=4)

