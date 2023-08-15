import sqlite3


def get_by_id(user_id: int):
    # Подключение к базе данных
    conn = sqlite3.connect('resources/users_yandex.db')
    cursor = conn.cursor()

    # Выполнение запроса
    query = f"SELECT * FROM users_data_yandex WHERE user_id = ? LIMIT 1"
    cursor.execute(query, (user_id,))

    # Извлечение данных
    user_data = cursor.fetchone()

    # Закрытие соединения
    conn.close()

    column_names = [description[0] for description in cursor.description]

    if user_data:
        # Создание словаря с данными
        user_data_dict = dict(zip(column_names, user_data))
    else:
        user_data_dict = "У этого пользователя нет активных заказов."

    return user_data_dict


print(get_by_id(7))