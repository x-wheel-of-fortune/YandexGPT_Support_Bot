import sqlite3


def get_by_id(user_id: int):
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

    column_names = [description[0] for description in cursor.description]

    # Создание словаря с данными
    user_data_dict = dict(zip(column_names, user_data))

    return user_data_dict


def main():
    # Пример использования
    user_id = 7  # Замените на нужный вам ID пользователя
    user_data = get_by_id(user_id)
    if user_data:
        print(user_data)
    else:
        print(f"Пользователь с ID {user_id} не найден.")


if __name__ == '__main__':
    main()
