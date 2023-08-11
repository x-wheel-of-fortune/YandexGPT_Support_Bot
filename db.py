import sqlite3


def get_user_data_by_id(user_id):
    # Подключение к базе данных
    conn = sqlite3.connect('users_yandex.db')
    cursor = conn.cursor()

    # Выполнение запроса
    query = f"SELECT * FROM users_data_yandex WHERE user_id = ?"
    cursor.execute(query, (user_id,))

    # Извлечение данных
    user_data = cursor.fetchone()

    # Закрытие соединения
    conn.close()

    return user_data


# Пример использования
user_id = 7  # Замените на нужный вам ID пользователя
user_data = get_user_data_by_id(user_id)
if user_data:
    print(user_data)
else:
    print(f"Пользователь с ID {user_id} не найден.")