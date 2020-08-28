import sqlite3

from core.log_manager import logger


class GenericModule:

    def create_tables(self, table):
        conn = sqlite3.connect("games.db")
        pointer = conn.cursor()

        pointer.execute(
            f"CREATE TABLE {table} (ID INTEGER PRIMARY KEY AUTOINCREMENT"
            f", NAME VARCHAR(50), LINK VARCHAR(100))"
        )
        conn.commit()
        logger.debug(f"Table '{table}' has been added to the database")

    def check_database(self, table, processed_data, threshold=10):

        free_games = []
        last_registries = []
        conn = sqlite3.connect("games.db")
        pointer = conn.cursor()

        try:
            try:  # Creates the table if It didn't exist already
                self.create_tables(table)
            except sqlite3.OperationalError:  # If the given table name already exists
                pass

            temp_last_registries = pointer.execute(f"SELECT NAME FROM {table} "
                                                   f"WHERE ID > (SELECT MAX(ID) - {threshold} FROM {table})")
            temp_last_registries = temp_last_registries.fetchall()

            for i in temp_last_registries:  # Cleans the output
                last_registries.append(i[0])

            try:
                for i in processed_data:
                    if i[0] not in last_registries:  # If name does not match any value in last_registries
                        free_games.append(i)

            except IndexError:
                logger.debug("Database empty")

            if not free_games:
                return False
            else:
                # Adds the registry of the game to the DB
                pointer.executemany(f"INSERT INTO {table} VALUES (NULL,?,?)", free_games)
                logger.info(f"New registry/ies added to the DB: {free_games}")
                return free_games

        finally:
            conn.commit()  # Saves changes
            conn.close()

    def get_free_games(self):
        return None
