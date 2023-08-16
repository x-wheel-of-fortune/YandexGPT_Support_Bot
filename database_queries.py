import sqlite3


class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()


def get_by_id(user_id: int):
    # Use context manager for the database connection
    with DatabaseConnection('resources/users_yandex.db') as conn:
        cursor = conn.cursor()

        query = f"SELECT * FROM users_data_yandex WHERE user_id = ?"
        cursor.execute(query, (user_id,))

        user_data = cursor.fetchone()

        column_names = [description[0] for description in cursor.description]

        if user_data:
            user_data_dict = dict(zip(column_names, user_data))
        else:
            user_data_dict = "У этого пользователя нет активных заказов."

        return user_data_dict


print(get_by_id(7))