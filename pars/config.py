import psycopg2
import requests


def get_connection():
    """Функция подключения приложения к базе данных."""
    conn = psycopg2.connect(
            host='localhost',
            user='postgres',
            password='postgres',
            database='task_parser'
    )
    return conn


def insert_data_task(nu, na, com_list, solv, th):
    """
    Функция для парсинга данных в таблицу task_info.

    :param nu - номера задач.
    :param na - названия задач.
    :param com_list - количество решения каждой задачи.
    :param solv - сложность каждой задачи.
    :param th - тема (темы) каждой задачи.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT into task_info '
                '(task_number,'
                'task_name, '
                'complexity_task, '
                'number_of_solved, '
                'task_theme) values (%s, %s, %s, %s, %s) '
                'ON CONFLICT (task_number) DO UPDATE '
                'SET complexity_task = EXCLUDED.complexity_task,'
                'number_of_solved = EXCLUDED.number_of_solved',
                (nu,
                 na,
                 com_list,
                 solv,
                 th))
    conn.commit()
    cur.close()
    conn.close()

