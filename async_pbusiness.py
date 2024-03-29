# -*- coding: utf-8 -*-
# !/usr/bin/env python3


import random
import asyncio
import aiohttp
from lxml import html
import re
import os
import socks
import socket


# чтобы работало через запущенный Тор - раскомментировать
# socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
# socket.socket = socks.socksocket

DOMAIN = 'https://p-business.ru'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
}


async def get_html_code(session, url):  # получение html кода с любой стр
    async with session.get(url, headers=headers) as response:
        try:
            response.encoding = 'utf8'
        except Exception:
            pass
        html_code = await response.text()
        return html_code


async def get_byte_code(session, url):  # получение byte кода с любой стр
    async with session.get(url, headers=headers) as response:
        try:
            response.encoding = 'utf8'
        except Exception:
            pass
        byte_code = await response.read()
        return byte_code


async def get_urls(session):
    url = 'https://p-business.ru/karta-sajta/'
    html_code = await get_html_code(session, url)
    dom_tree = html.fromstring(html_code)
    urls = dom_tree.xpath("//*[@id='sitemap_list']//ul/li/a/@href")  # 1455
    return urls  # список всех урлов с карты сайта


async def get_folder(session, html_code, url):
    dom_tree = html.fromstring(html_code)
    folder = dom_tree.xpath('//title')[0].text  # имя папки с файлами
    if len(folder) > 1:  # если тайтл не пустой
        folder = re.sub('\W+', ' ', folder)  # удаляет спецсимволы из строки
        if len(folder) >= 45:  # чтобы имя папки было не очень большим
            folder = folder[:45]
    else:  # если тайтл пустой
        folder = url.split('/')[-2]
    if not os.path.exists(folder):  # если такой папки нету
        os.makedirs(folder)  # создаем ее
    return folder


async def get_img_urls(session, html_code):  # +
    dom_tree = html.fromstring(html_code)
    img_links = dom_tree.xpath("//div[@class='entry']//img/@src")
    return img_links  # список всех урлов статьи, ведущих на картинки


async def save_img(session, img_url, folder):
    print(f'Продолжаем с {folder}')
    try:
        response = await get_byte_code(session, img_url)
        name = img_url.split('/')[-1]
        await asyncio.sleep(2)
        write_img(response, name, folder)
    except FileNotFoundError as err:
        print('Картинка не скачивается', img_url, err)
        pass
    except Exception as err:
        print(err, type(err))


def write_img(response, name, folder):
    with open(f'{folder}/{name}', 'wb') as pic:
        pic.write(response)


async def parse_url(session, url, sem):  # +
    async with sem:
        for i in range(3):
            print('-' * 30)
            print(f'Парсинг {i+1}', url)
            try:
                await asyncio.sleep(2)
                html_code = await get_html_code(session, url)
                folder = await get_folder(session, html_code, url)
                img_urls = await get_img_urls(session, html_code)
                for img_url in img_urls:
                    # сохранение img в файл
                    await save_img(session, img_url, folder)

            except ConnectionError as e:
                print('Ошибка на ссылке', url, e)
                await asyncio.sleep(10)

            except aiohttp.client_exceptions.ServerDisconnectedError as err:
                print('Сервер разорвал коннект', url, err)
                await asyncio.sleep(30)

            except aiohttp.client_exceptions.ClientConnectorError as err:
                print('Превышен таймаут семафора', url, err)
                await asyncio.sleep(30)

            except asyncio.exceptions.TimeoutError as err:
                print('TimeoutError', url, err)
                await asyncio.sleep(30)

            except Exception as ex:
                print('Ошибка', ex)
                await asyncio.sleep(10)


async def run():  # +
    async with aiohttp.ClientSession() as session:
        sem = asyncio.Semaphore(5)
        urls = await get_urls(session)
        tasks = []
        for url in urls:
            task = asyncio.create_task(parse_url(session, url, sem))
            tasks.append(task)
        await asyncio.gather(*tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
