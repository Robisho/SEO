# -*- coding: utf-8 -*-
# !/usr/bin/env python3

import random
import asyncio
import aiohttp
from lxml import html

import json
from time import sleep


DOMAIN = 'https://leroymerlin.ru'
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
    }


async def get_html(session, url):  # получение html кода с любой стр
    async with session.get(url, headers=headers) as response:
        html_code = await response.text()
    return html_code


async def home_page(session):  # получение ссылок основных категорий
    url = 'https://leroymerlin.ru/catalogue/'
    category_list = []
    content = await get_html(session, url)
    dom_tree = html.fromstring(content)

    hrefs = dom_tree.xpath("//nav[@class='leftmenu-small']//li/a/@href")[:-1]
    for href in hrefs:  # последние ссылки баннеры рекламные
        link = DOMAIN + href
        category_list.append(link)
    # print(category_list)
    return category_list


async def category_page(session, url):  # получение ссылок из категорий/субкатегорий
    # x = random.randint(1, 2)
    await asyncio.sleep(1)
    content = await get_html(session, url)
    dom_tree = html.fromstring(content)

    link_list = []
    main_list = dom_tree.xpath('.//uc-catalog-facet-link')
    for i, el in enumerate(main_list, 0):
        href = dom_tree.xpath('.//uc-catalog-facet-link/a/@href')[i]
        link = DOMAIN + href
        link_list.append(link)  # список линков из категории/субкатегории
        # print(link)
    return link_list


# все результаты сразу пишутся в файл в функции page()
async def product_page(session, url):  # парсинг самой страницы со списком товаров
    # data_list = []
    x = random.randint(1, 2)
    await asyncio.sleep(x)  # на всякий случай) можно убрать
    content = await get_html(session, url)
    dom_tree = html.fromstring(content)

    paginator = dom_tree.xpath('.//div[@class="list-paginator"]')  # +
    # print(paginator)
    if paginator:
        count = (paginator.xpath(".//div[@class='item-wrapper']/a")[-1]).text
        for i in range(1, int(count)+1):
            url_page = url + f'?sortby=8&page={i}'
            result = await page(session, url_page)  # список всех товаров со страницы
    else:
        result = await page(session, url)  # список всех товаров со страницы


async def page(session, url):  # парсинг карточки с товаром
    x = random.randint(1, 2)
    await asyncio.sleep(x)  # на всякий случай) можно убрать
    content = await get_html(session, url)
    dom_tree = html.fromstring(content)

    product_list = dom_tree.xpath('.//product-card')
    for i, product in enumerate(product_list, 0):

        titles = dom_tree.xpath('.//product-card/@product-name')
        for t in titles:
            title = titles[i]

        categories = dom_tree.xpath('.//product-card/@data-category')
        for c in categories:
            category = categories[i]

        urls = dom_tree.xpath('.//product-card/@data-product-url')
        for u in urls:
            url = urls[i]
            link = DOMAIN + url

        img_list = product.xpath(".//picture/img[@class='plp-item-picture__image']/@src")
        for pic in img_list:
            img = pic.split(' ')[0]

        data = {
            'title': title,
            'category': category,
            'link': link,
            'img': img
        }

        with open('res_leroymerlin.json', 'a', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)


async def run():
    async with aiohttp.ClientSession() as session:
        subcat_list, subsubcat_list = [], []
        category_list = await home_page(session)  # получили список ссылок категорий
        # print(category_list)  # 17 категорий

        for cat in category_list:
            subcat = await category_page(session, cat)  # список ссылок подкатегорий
            subcat_list.append(subcat)

        for llist in subcat_list:  # из списка списков берем список ссылок
            for num in llist:  # из списка берем каждую ссылку
                result = await product_page(session, num)  # получаем список товаров со страницы
                print(f'парсим {num}')  # добавлено для наглядности работы парсера


async def main():
    task = asyncio.ensure_future(run())
    await asyncio.gather(task)

    sleep(0.1)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())  # а так норм работает!
