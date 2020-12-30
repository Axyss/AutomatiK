import sqlite3
from core.log_manager import logger


class Game:
    def __init__(self, name, link):
        self.name = name
        self.link = link

    def __eq__(self, other):
        return True if self.name == other.name else False


class DBManager:

    DB_NAME = "games.db"

    def __init__(self):
        self.conn = None
        self.pointer = None

    def connect_to_db(self):
        self.conn = sqlite3.connect(DBManager.DB_NAME)
        self.pointer = self.conn.cursor()
        logger.debug("Connection established to the database")

    def disconnect_from_db(self):
        self.conn.commit()
        self.conn.close()
        logger.debug("Connection to the database closed")

    def create_table(self, table):
        self.connect_to_db()
        try:
            self.pointer.execute(
                f"CREATE TABLE {table} (ID INTEGER PRIMARY KEY AUTOINCREMENT"
                f", NAME VARCHAR(50), LINK VARCHAR(100))"
            )
        except sqlite3.OperationalError:
            return False
        finally:
            self.disconnect_from_db()
        logger.debug(f"Table '{table}' has been added to the database")
        return True

    def check_database(self, table, input_data, threshold):
        free_games, last_reg = [], []
        self.create_table(table)
        self.connect_to_db()

        last_reg = self.pointer.execute(f"SELECT NAME, LINK FROM {table} "
                                        f"WHERE ID > (SELECT MAX(ID) - {threshold} FROM {table})")
        last_reg = last_reg.fetchall()

        try:
            last_reg = tuple(map(lambda x: Game(x[0], x[1]), last_reg))  # Contains last n games of the db
            free_games = tuple(filter(lambda x: x not in last_reg, input_data))  # Removes already added games
        except IndexError:
            logger.debug("Database empty")

        self.pointer.executemany(f"INSERT INTO {table} VALUES (NULL,?,?)",
                                 [(game.name, game.link) for game in free_games])
        logger.info(f"New registry/ies added to the DB: "
                    f"{[(game.name, game.link) for game in free_games]}") if free_games else None
        self.disconnect_from_db()
        return free_games


db = DBManager()
