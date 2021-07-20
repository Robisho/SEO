# -*- coding: utf-8 -*-
#!/usr/bin/env python3

'''
requests
По ссылке https://line11.bkfon-resources.com/live/currentLine/ru получить все футбольные матчи в Лайве.
Данные записать в словарь по названию игроков в виде gamer_name = "Игрок 1 - Игрок 2".
Словарь должен быть в ввиде: {id1: gamer_name1, id2: gamer_name2, .... idN: gamer_nameN}
id - уникальный идентификатор в md5
Для получения идентификатора использовать модуль hashlib

selenium
Из полученных данных выбрать любую игру. в Браузере через Selenium открыть игру по названию (не по url).
В консоль вывести название выбранной игры.
Использовать Chrome.
'''

import hashlib
import requests
import time
import requests_random_user_agent
from selenium import webdriver


source_url = 'https://line11.bkfon-resources.com/live/currentLine/ru'
game_select_url = 'https://www.fonbet.ru/sports/football/12764'
gamer_name = 'Динамо Загреб — Омония Никосия'


def get_soccer_games(source_url):
    with requests.Session() as session:
        headers = session.headers
        response = session.get(source_url, headers=headers)
        if response.status_code != 200:
            print('Неудачное соединение', f'{response.status_code}')

        else:
            content = response.json()
            main_list = content['announcements']
            soccer_games = {}

            for item in main_list:
                if item['sportName'] == 'Футбол':
                    gamer_name = f"{item['team1']} — {item.setdefault('team2', [])}"
                    hash_obj = hashlib.md5(gamer_name.encode())
                    id = hash_obj.hexdigest()
                    soccer_games[id] = gamer_name

        with open('soccer_games.txt', 'w') as file:
            for key, val in soccer_games.items():
                file.write(f'{key}: {val}\n')


def select_game(game_select_url, gamer_name):
    driver = webdriver.Chrome()
    driver.get(game_select_url)
    time.sleep(5)
    try:
        link = driver.find_element_by_link_text(gamer_name)
        link.click()
        print(gamer_name)
    except:
        print('Элемент не найден')
    finally:
        time.sleep(5)
        driver.quit()


if __name__ == '__main__':
    get_soccer_games(source_url)
    select_game(game_select_url, gamer_name)
