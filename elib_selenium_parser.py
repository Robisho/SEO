# -*- coding: utf-8 -*-
# !/usr/bin/env python3
'''
# Парсер elibrary.ru на selenium, получение ссылок вида
# https://elibrary.ru/item.asp?id=28153408 по ключевому слову
#
'''

from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import csv

# keyword = ''
keyword = 'Московкин Леонид'
# keyword = 'КРЕМНЁВ ЕВГЕНИЙ ВЛАДИМИРОВИЧ'  # 107

def init_driver():  # инициализация экземпляра драйвера
    driver = webdriver.Firefox()  # создался драйвер
    driver.implicitly_wait(3)
    return driver


def input_key(driver, keyword):  # получаем выдачу по ключу
    driver.get('https://www.elibrary.ru/defaultx.asp')  # начальная пага
    fild = driver.find_element_by_class_name('inputt')  # id='ftext'
    enter = driver.find_element_by_class_name('butblue')  #
    fild.send_keys(keyword)
    sleep(3)
    enter.click()


def get_html(url):  # получаем код страницы
    r = driver.get(url)
    html = driver.page_source
    return html


# def write_csv(data):
#     with open('elib_parse.csv', 'a') as f:
#         writer = csv.writer(f)
#         writer.writerow((data['link'], data['index']))


def parse(url):  # сам парсинг
    result = []
    # получаем html из url
    soup = BeautifulSoup(get_html(url), 'lxml')
    trs = soup.find('table', id='restab').find_all('tr')  # собираем все tr

    for tr in trs[1:]:  # для всех tr, кроме первого
        # id = tr.get('id')  # берем id этого tr
        tds = tr.find_all('td')  # собираем для этого tr все td
        # у второго td ищем a и берем его href
        href = tds[1].find('a').get('href')
        link = 'https://elibrary.ru' + href  # формируем валидную ссыль
        index = int(tds[-1].text)  # индекс - из последнего td
        data = (link, index)  # записываем в кортеж
        result.append(data)  # кортеж добавляем в список

        # data = {'link': link,
        #         'index': index}

        # write_csv(data)
        # sleep(2)

    return result


def main():
    url = 'https://elibrary.ru/query_results.asp'
    result = parse(url)  # запускается сам парсинг

    while True:
        soup = BeautifulSoup(get_html(url), 'lxml')

        try:  # если страниц выдачи больше одной
            tds = soup.find('tr', class_='menus').find_all('td')
            href = tds[-2].find('a').get('href')
            url = 'https://elibrary.ru/' + href
            res = parse(url)
            result += res
        except:  # иначе выдача только с одной страницы
            break

    return result  # весь результат парсинга, список кортежей


if __name__ == "__main__":
    try:
        driver = init_driver()  # инициализация драйвера
        input_key(driver, keyword)  # получаем выдачу по ключу
        print('Результаты по запросу ', keyword)

        result = main()  # сам парсинг, получаем список кортежей
        # сортируем список по второму элементу кортежей
        result.sort(key=lambda x: x[1])
        result.reverse()  # реверснули список, чтобы вначале был максимальный индекс

        for i in result:
            print(i[0], ':', i[1])

        print('Получено всего статей ', len(result))

    finally:
        driver.quit()
