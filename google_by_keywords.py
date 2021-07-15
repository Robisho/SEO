# -*- coding: utf-8 -*-
#!/usr/bin/env python3

'''
получение из топа гугла статьи по ключу,
вид статьи: текст с тегами разметки, если нужен голый текст статьи - нужно убрать начиная со 155 строки теги в цикле for,
анализ верстки статьи на основе if <p> > 5
'''

import re
import os
import requests
from bs4 import BeautifulSoup
from random import randint
from time import sleep
import requests_random_user_agent

from google_stopdomens import STOPDOMENS


def get_html_code(session, headers, url, attempts=3):
    a = attempts
    print('Попыток get запроса ', a)
    try:
        response = session.get(url, headers=headers)
        response.encoding = 'utf8'
        return response
    except Exception as e:
        print(e, type(e))
        print('Ошибка при get запросе')
        if a > 1:
            a -= 1
            sleep(60)
            get_html_code(session, headers, url, a)


def get_urls(session, headers, keyword, attempts=3):
    a = attempts
    url = f'https://www.google.com/search?q={keyword}'
    print('Попыток получения списка доменов ', a)
    try:
        resp = get_html_code(session, headers, url)
        soup = BeautifulSoup(resp.text, 'lxml')

        urls = []
        divs = soup.find_all("div", class_='yuRUbf')
        for div in divs:
            url = div.find('a').get('href')
            urls.append(url)

        return urls
    except Exception as e:
        print(e, type(e))
        print('Получение списка доменов не удалось')
        if a > 1:
            a -= 1
            sleep(60)
            get_urls(session, headers, keyword, a)


def get_article(session, headers, url):
    resp = get_html_code(session, headers, url)
    soup = BeautifulSoup(resp.text, 'lxml')
    title = soup.find('title').text
    if len(title) > 1:
        title = re.sub('\W+',' ', title) # удаляет спецсимволы из строки
        if len(title) >= 60:
            title = title[:60]
    else:
        title = url.split('/')[-2]

    try:
        h1 = soup.find('h1').text.strip()
    except:
        h1 = title

    tag1 = soup.find('article')
    tag2 = soup.find('main', {'class': True})
    tag3 = soup.find('div', itemtype='http://schema.org/Article')
    tag4 = soup.find('div', itemprop=re.compile('articleBody'))

    patt_content = re.compile('[Cc]ontent')
    patt_inner = re.compile('[Ii]nner')
    patt_footer = re.compile('[Ff]ooter')
    patt_comment = re.compile('[Cc]omment')

    div_list = soup.find_all('div')

    tag_list = []
    tag_list.append(tag1)
    tag_list.append(tag2)
    tag_list.append(tag3)
    tag_list.append(tag4)

    for tag in tag_list:
        if tag:
            if len(tag.find_all('p')) > 5:
                article_tag = tag
                break
    else:
        for div in div_list:
            # исключаем class="comment" & class="footer"
            if not re.search(f'{patt_footer}|{patt_comment}', ' '.join(div.attrs.get('class', []))):
                if len(div.find_all('p')) > 5:
                    # print(div.name, div.attrs)
                    # print('2-' * 10)  # для наглядности вывода в консоль

                    if div.has_attr('id'):
                        if re.search(patt_content, ''.join(div.attrs['id'])):
                            article_tag = div

                        elif 'article' in div.attrs['id']:
                            article_tag = div

                        elif 'main' in div.attrs['id']:
                            article_tag = div

                    elif div.has_attr('class'):
                        if re.search('article', ' '.join(div.attrs['class'])):
                            article_tag = div

                        elif re.search(patt_content, ' '.join(div.attrs['class'])):
                            article_tag = div

                        elif re.search(patt_inner, ' '.join(div.attrs['class'])):
                            article_tag = div

                        elif re.search('main', ' '.join(div.attrs['class'])):
                            article_tag = div

                        elif re.search('post-page', ' '.join(div.attrs['class'])):
                            article_tag = div

                        elif re.search('single-post', ' '.join(div.attrs['class'])):
                            article_tag = div

                        elif re.search('formatedTexts', ' '.join(div.attrs['class'])):
                            article_tag = div

                        elif re.search('entry', ' '.join(div.attrs['class'])):
                            article_tag = div

    '''
    TO DO: отдельную фунцию, если тег не определен - берем другой урл
    '''
    article_tags_list = []
    try:
        article_tags_list = article_tag.find_all(['h2', 'h3', 'h4', 'p', 'ul', 'ol', 'figure', 'table', 'div'])
        print('тег статьи ', article_tag.name, article_tag.attrs)
        # тоже для наглядности
    except:
        print('Тег статьи не определен!')

    article = ''
    for t in article_tags_list:
        try:
            if t.name == 'p':
                if t.find('img') is not None:
                    img_attrs = str(t.find('img'))
                    link = re.search('(?<=src=\")\S+(?=\")', img_attrs)[0]
                    article += '\n'+ f'<img src="{link}" />' +'\n'

                if t.text.strip():
                    article += '\n' + f'<{t.name}>'+ t.text.strip() + f'</{t.name}>' + '\n'

            elif t.name == 'ul' or t.name == 'ol':
                if t.find_all('li') is not None:
                    article += '\n'
                    for l in t.find_all('li'):
                        article += f'<{l.name}>'+ l.text.strip() + f'</{l.name}>' + '\n'

            elif t.name == 'figure':
                if t.find('img') is not None:
                    img_attrs = str(t.find('img'))
                    link = re.search('(?<=src=\")\S+(?=\")', img_attrs)[0]
                    article += '\n'+ f'<img src="{link}" />' +'\n'

            elif t.name == 'div':
                if t.find('img') is not None:
                    img_attrs = str(t.find('img'))
                    link = re.search('(?<=src=\")\S+(?=\")', img_attrs)[0]
                    article += '\n'+ f'<img src="{link}" />' +'\n'

            elif t.name == 'table':
                article += '\n' + '<p>' + f'<{t.name}>' + '<tbody>' + '\n'
                if t.find_all('tr') is not None:
                    for tr in t.find_all('tr'):
                        article += str(tr) + '\n'
                article += '</tbody>' + f'</{t.name}>' + '</p>' + '\n'

            else:
                article += '\n' + f'<{t.name}>'+ t.text.strip() + f'</{t.name}>' + '\n'

        except Exception as e:
            print(e, type(e))
            print('Ошибка в получении статьи ')
            continue

    write_article(h1, title, article, url)


def write_article(h1, title, article, url):
    file_name = f'{title}' + '.txt'
    file = open(file_name, 'w+', encoding='utf-8')
    file.write(f'<h1>{h1}</h1>')
    file.write('\n\n')
    file.write(article)
    file.write('#############################')
    file.write('\n\n')
    file.write(f'{url}')
    file.close()


def parse():
    with open('keywords.txt', 'r', encoding='utf-8') as file:
        key_list = file.readlines()

    # при обрыве парсинга начать с нужного ключа key_list[479:]
    for i, keyword in enumerate(key_list, start=1):
        with requests.Session() as session:
            print('-' * 30)  # для наглядности вывода в консоль
            headers = session.headers  # ramdom headers каждый requests
            sleep(randint(60, 65))  # интервал, чтобы гугл не банил
            print(i, f'Собираем выдачу: {keyword}')
            urls = get_urls(session, headers, keyword) # выдача по ключу
            print(urls)

            bad_urls = []
            # убираем сайты из стоп-листа
            # TO DO: пофиксить, если доменов нету!!!
            for url in urls:
                for domain in STOPDOMENS:
                    if url.find(domain) != -1:
                        bad_urls.append(url)
            # остались те, что не в стоп-листе
            good_urls = list(set(urls).difference(set(bad_urls)))
            print(good_urls)

            for url in good_urls[:1]:  # сколько статей берем
                try:
                    sleep(randint(5, 7))
                    print(f'Статья c {url}')
                    get_article(session, headers, url)

                except FileNotFoundError as e:
                    print(e, type(e))
                    print('Не нашлась статья для скачивания')
                    continue

                except requests.exceptions.SSLError as e:
                    print(e, type(e))
                    print('Ошибка сертификата')
                    continue

                except Exception as e:
                    print(e, type(e))
                    print('Неизвестная ошибка при получении статьи')
                    continue


if __name__ == '__main__':
    parse()

