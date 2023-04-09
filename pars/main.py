import time
import asyncio

import requests
import lxml.html
import schedule

from bs4 import BeautifulSoup
from lxml import etree

import config


start_url = "https://codeforces.com/problemset/page/1?order=" \
      "BY_SOLVED_DESC"


def scrape_page():
    """Для обхода всех страниц и получения html информации."""
    for numb in range(1, 87):
        url = "https://codeforces.com/problemset/page/{}?order=" \
              "BY_SOLVED_DESC".format(numb)
        tree = lxml.html.document_fromstring(requests.get(url).text)
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        asyncio.run(get_data(soup, tree))


async def get_data(soup, tree):
    """
    Функция для получения контента номера, названия, сложности, количества
    решений каждой задачи с каждой страницы и дальнейшая передача для
    загрузки в БД.

    Принимает на вход следующие аргументы:
    :param soup - библиотека для извлечения данных из XML и HTML страниц.
    :param tree - служит для обработки разметки XML и HTML страниц.
    """
    # Получаем полный перечень номеров задач с каждой страницы
    # и сохраняем в списке task_list
    data = soup.find_all('td', attrs={'class': 'id'})

    task_list = []
    task_number = soup.find_all("td", class_="id")
    for num in task_number:
        task_list.append(num.text.strip())

    # Получаем полный перечень названий задач с каждой страницы
    # и сохраняем в списке name_list
    name_list = []
    task_name = tree.xpath("//div//div//div//div//table//tr//td//div/"
                           "a[contains(@href, 'problemset/problem')]/text()")
    for nam in task_name:
        name_list.append(nam.strip())

    # Получаем полный перечень сложности каждой задачи
    # с каждой страницы и сохраняем в списке comp_list
    comp_list = []
    complexity_task = [element.find_next('td').find_next('td').find_next(
                       'td').span.text if element.find_next('td').find_next(
                       'td').find_next('td').span else ' ' for element in data]
    for complexity in complexity_task:
        comp_list.append(complexity)

    # Получаем полный перечень количества решений каждой задачи
    # с каждой страницы и сохраняем в списке solv_list
    solv_list = []
    for element in data:
        info = element.find_next('td').find_next('td').find_next(
            'td').find_next('td')
        if info.a:
            solv_list.append(info.a.text)
        else:
            solv_list.append(' ')

    theme = []
    # Получаем полный перечень тем с каждой страницы
    task_theme = ([el.text for el in element.find_next('td').div.find_next(
                  'div').find_all('a')] for element in data)
    for them in task_theme:
        theme.append(them)

    for index in range(0, len(task_list)):
        nu = task_list[index]
        na = name_list[index]
        com_list = comp_list[index]
        solv = solv_list[index]
        th = theme[index]

        # Передача данных для загрузки в таблицу task_info
        config.insert_data_task(nu, na, com_list, solv, ', '.join(th))


def main():
    scrape_page()


if __name__ == "__main__":
    schedule.every(1).hour.do(main)
