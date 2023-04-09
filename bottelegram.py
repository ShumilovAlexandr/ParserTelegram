import os

from dotenv import load_dotenv
from keyboa import Keyboa

import telebot

from pars.config import get_connection

load_dotenv()

API_TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(API_TOKEN)


# Для хранения результата выбора сложности в handle_difficulty_selection
difficulty = None


@bot.message_handler(commands=['start'])
def start_bot(message):
    """
    Стартовая функция запуска бота.

    Функция выводит на экран набор кнопок с указанием в каждой уровня
    сложности.
    """
    number = get_difficulty()
    buttons = Keyboa(items=number, items_in_row=6, copy_text_to_callback=True)
    bot.send_message(message.chat.id, text="Выбери сложность задания.",
                     reply_markup=buttons())


@bot.callback_query_handler(func=lambda call: call.data in get_difficulty())
def handle_difficulty_selection(call):
    """
    Функция обрабатывает выбор сложности.
    """
    global difficulty
    difficulty = call.data
    topics = get_themes()
    buttons = Keyboa(items=topics, items_in_row=2)
    bot.send_message(call.message.chat.id, text="Выбери тему задания",
                     reply_markup=buttons())


@bot.callback_query_handler(func=lambda call2: call2.data in get_themes())
def handle_topic_selection(call2):
    """
    Обрабатывает выбор темы задания.
    """
    theme = call2.data
    # Используем тему для получения подходящих значений из базы данных
    values = get_values(difficulty, theme)
    # Отправляем 10 подходящих значений пользователю
    bot.send_message(call2.message.chat.id,
                     text="Подходящие задачи: " + str(values))


###############################################################################
def get_difficulty():
    """
    Функция для получения всех значений сложности задач.

    :return: функция возвращает список неповторяющихся уникальных
    значений сложности задач.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT complexity_task FROM task_info '
                'ORDER BY complexity_task')
    row = cur.fetchall()

    # В списке будут храниться строки со всеми сложностями к каждой задаче.
    numb = []

    # В списке num будут храниться уникальные значения сложности.
    num = []
    # Тут кортежи преобразоваются в строки и записываются в список для
    # дальнейшей удобной работы.
    for i in row:
        numb.append(''.join(i))

    # Проходим по каждому слову в строке
    for n in numb:
        if n.strip() != '':
            num.append(n)
    return num


def get_themes():
    """
    Функция для возврата всех тем уникальных тем заданий.

    :return: возвращает список words_list с неповторяющимися уникальными
    темами для задач.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT task_theme FROM task_info')
    row = cur.fetchall()

    # В списке будут храниться строки со всеми темами к каждой задаче.
    theme = []

    # В списке words_list будут храниться уникальные значения тем.
    words_list = []

    for x in row:
        # Тут кортежи преобразовываются в строки и записываются в список для
        # дальнейшей удобной работы.
        theme.append(''.join(x))

    # Здесь осуществляется проход по каждой строке в списке
    for string in theme:
        # Разбиение каждой строки по запятой
        words = string.split(',')
        # Проходим по каждому слову в строке
        for word in words:
            if word.strip() not in words_list:
                if word.strip() != '':
                    words_list.append(word.strip())
    return words_list


###############################################################################


def get_values(diff, theme):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT task_number, task_name, complexity_task, '
                'number_of_solved, task_theme FROM task_info WHERE '
                'complexity_task = %s AND task_theme LIKE %s'
                'ORDER BY RANDOM() LIMIT 10', (f"{diff}",
                                               f"%{theme}%"))
    row = cur.fetchall()
    return row


# bot.infinity_polling()
