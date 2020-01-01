import requests
import sqlite3
import time


class Scraping:

    def __init__(self):

        self.source = "https://www.humblebundle.com/store/api/search?sort=discount&filter=onsale&request=1"
        self.baseUrl = "https://www.humblebundle.com/store/"
        self.gameData = []  # Data from free games (name, link)
        self.validGameData = []  # Verified games from the DB method

        self.data = None

    def reset_request(self):

        self.gameData = []
        self.data = None
        self.validGameData = []

    def make_request(self):
        """Makes the request and removes the unnecessary JSON data"""

        self.reset_request()

        try:
            self.data = requests.get(self.source).json()

        except:
            print(time.strftime('[%Y/%m/%d]' + '[%H:%M]') +
                  "[ERROR]: Humble Bundle request failed!")

        self.data = self.data["results"]

    def process_request(self):  # Filters games that are not free
        """Returns the useful information form the request"""

        for i in self.data:

            if i["current_price"]["amount"] == 0:  # If game's price is 0

                # Parses relevant data such as name and link and adds It to gameData
                temp = (i["human_name"], str(self.baseUrl + i["human_url"]))

                self.gameData.append(temp)

    def check_database(self):
        """Manages the DB"""

        # Opens DB connection.
        conex = sqlite3.connect("db")
        pointer = conex.cursor()

        try:
            # Tries to create the table if doesn't exist
            try:
                pointer.execute(
                    "CREATE TABLE TABLA_2 (ID INTEGER PRIMARY KEY AUTOINCREMENT, NOMBRE VARCHAR(50), LINK VARCHAR(100))"
                )  # This line will create the table If It didn't already exist
                conex.commit()

            except sqlite3.OperationalError:  # If that table name already exists.
                pass

            cache = pointer.execute("SELECT NOMBRE FROM TABLA_2 WHERE ID > (SELECT MAX(ID) - 5 FROM TABLA_2)")
            cache = cache.fetchall()
            cache2 = []  # Here the information from the query is cleaned.

            for i in cache:  # Tuples are removed here
                cache2.append(i[0])

            # If there is no cache or the game is already in the DB then skip...
            try:

                for i in self.gameData:

                    if i[0] not in cache2:  # If param 0 does not match any of the DB then It's a new game.

                        self.validGameData.append(i)  # Adds the data to a new list

            except IndexError:
                print("[ERROR]: Empty database")

            if not self.validGameData:  # If validGameData empty return
                return None

            # Adds the register of the game to the DB
            pointer.executemany("INSERT INTO TABLA_2 VALUES (NULL,?,?)", self.validGameData)  # Iterates the

            print(time.strftime('[%Y/%m/%d]' + '[%H:%M]') +
                  "[DB]: New register added:",
                  self.validGameData
                  )

            return True  # If there games not registered in the database

        # Closes connection under any circumstances
        finally:
            conex.commit()  # Saves changes
            conex.close()


obj = Scraping()
