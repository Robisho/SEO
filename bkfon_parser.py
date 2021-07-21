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
import random
import requests
import time
import requests_random_user_agent
from selenium import webdriver


source_url = 'https://line11.bkfon-resources.com/live/currentLine/ru'
game_select_url = 'https://www.fonbet.ru/live'


def get_soccer_games(source_url):
    with requests.Session() as session:
        headers = session.headers
        response = session.get(source_url, headers=headers)
        if response.status_code != 200:
            print('Неудачное соединение', f'{response.status_code}')
        else:
            content = response.json()

            sports_list = content['sports']
            id_list = []

            soccer_id = 1
            for sport in sports_list:
                if sport.get('parentId'):
                    if sport['parentId'] == soccer_id:
                        id_list.append(sport['id'])

            main_list = content['events']
            soccer_games = {}

            for item in main_list:
                if item['team1Id'] and item['sportId'] in id_list:
                    gamer_name = f"{item['team1']} — {item['team2']}"
                    hash_obj = hashlib.md5(gamer_name.encode())
                    id = hash_obj.hexdigest()
                    soccer_games[id] = gamer_name

            return(soccer_games)


def get_gamer_name():
    '''
    выбор рандомной игры
    '''
    soccer_games = get_soccer_games(source_url)
    id, gamer_name = random.choice(list(soccer_games.items()))
    return gamer_name


def select_game(game_select_url):
    gamer_name = get_gamer_name()
    driver = webdriver.Chrome()
    driver.get(game_select_url)
    time.sleep(5)
    try:
        search = driver.find_element_by_xpath("//div[@class='search']/a").click()
        input_text = driver.find_element_by_xpath("//div[@id='search-component']/input").send_keys(f'{gamer_name}')
        time.sleep(2)
        link = driver.find_element_by_xpath('//a[contains(@class, "search-result__event-name")]').click()
        print(gamer_name)
    except:
        print('Элемент не найден')
    finally:
        time.sleep(5)
        driver.quit()


if __name__ == '__main__':
    select_game(game_select_url)
