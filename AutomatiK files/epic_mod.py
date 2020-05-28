import requests
import sqlite3
import time
import json


class Scraping:

    def __init__(self):

        self.baseUrl = "https://www.epicgames.com/store/es-ES/product/"
        self.gameData = []  # Data from free games (name, link)
        self.validGameData = []  # Verified games from the DB method

        self.endpoint = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=es-ES&country" \
                        "=ES&allowCountries=ES "

        self.data = None

    def reset_request(self):

        self.gameData = []
        self.data = None
        self.validGameData = []

    def make_request(self):
        """Makes the request and removes the unnecessary JSON data"""

        self.reset_request()

        try:
            self.data = requests.get(self.endpoint)

            self.data = json.loads(self.data.content)  # Bytes to json object

        except:
            print(time.strftime('[%Y/%m/%d]' + '[%H:%M]') +
                  "[ERROR]: Epic Games request failed!")

        # Removes the not relevant information from the JSON object
        self.data = self.data["data"]["Catalog"]["searchStore"]["elements"]

    def process_request(self):  # Filters games that are not free
        """Returns the useful information form the request"""

        for i in self.data:

            discountPrice = i["price"]["totalPrice"]["discountPrice"]

            if i["productSlug"] == "[]":  # If the game isn't free or listed
                continue

            # Parses relevant data such as name and link and adds It to gameData
            temp = (i["title"], str(self.baseUrl + i["urlSlug"]))

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
                    "CREATE TABLE TABLA_1 (ID INTEGER PRIMARY KEY AUTOINCREMENT, NOMBRE VARCHAR(50), LINK VARCHAR(100))"
                )  # This line will create the table If It didn't already exist
                conex.commit()

            except sqlite3.OperationalError:  # If that table name already exists.
                pass

            cache = pointer.execute("SELECT NOMBRE FROM TABLA_1 WHERE ID > (SELECT MAX(ID) - 8 FROM TABLA_1)")
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
                print(time.strftime('[%Y/%m/%d]' + '[%H:%M]') +
                      "[ERROR]: Empty database")

            if not self.validGameData:  # If validGameData empty return
                return None

            # Adds the register of the game to the DB
            pointer.executemany("INSERT INTO TABLA_1 VALUES (NULL,?,?)", self.validGameData)  # Iterates the

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
