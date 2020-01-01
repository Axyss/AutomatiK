import requests
import json
import sqlite3
import time


class Scraping:

    def __init__(self):

        self.route = ["data",
                      "Catalog",
                      "catalogOffer",
                      "collectionOffers"
                      ]
        self.gameData = []  # Data from free games (name, link)

        # QUERY VARS

        self.endpoint = "https://graphql.epicgames.com/graphql"
        self.gamesCollectionQuery = {
            "query": "\n            query catalogQuery($productNamespace:String!, $offerId:String!, $locale:String, "
                     "$country:String!) {\n                Catalog {\n                    catalogOffer(namespace: "
                     "$productNamespace, id: $offerId, locale: $locale) {\n                        title\n            "
                     "            collectionOffers {\n                            \n          title\n          id\n   "
                     "       namespace\n          description\n          keyImages {\n            type\n            "
                     "url\n          }\n          seller {\n              id\n              name\n          }\n       "
                     "   urlSlug\n          items {\n            id\n            namespace\n          }\n          "
                     "customAttributes {\n            key\n            value\n          }\n          categories {\n   "
                     "         path\n          }\n          price(country: $country) {\n            totalPrice {\n    "
                     "          discountPrice\n              originalPrice\n              voucherDiscount\n           "
                     "   discount\n              fmtPrice(locale: $locale) {\n                originalPrice\n         "
                     "       discountPrice\n                intermediatePrice\n              }\n            }\n       "
                     "     lineOffers {\n              appliedRules {\n                id\n                endDate\n  "
                     "            }\n            }\n          }\n          linkedOfferId\n          linkedOffer {\n   "
                     "         effectiveDate\n            customAttributes {\n              key\n              "
                     "value\n            }\n          }\n        \n                        }\n                        "
                     "customAttributes {\n                            key\n                            value\n        "
                     "                }\n                    }\n                }\n            }\n        ",
            "variables": {
                "productNamespace": "epic",
                "offerId": "7f22b3b15abc4821bba634340e2dd1ef",
                "locale": "es-ES",
                "country": "EN"
            }
        }
        self.rawData = ""
        self.data = None
        self.currentRoute = ""

    def reset_request(self):

        # Epic product does not go here

        self.gameData = []

        # QUERY VARS

        self.rawData = ""
        self.data = None
        self.currentRoute = ""

    def make_request(self):
        """Makes the request and saves It in a JSON object"""

        self.reset_request()
        # QUERY
        try:
            self.data = requests.post(self.endpoint, headers={"Content-type": "application/json;charset=UTF-8"
                                                              }, data=json.dumps(self.gamesCollectionQuery))
            self.rawData = json.loads(self.data.content)

        except:
            print(time.strftime('[%Y/%m/%d]' + '[%H:%M]') +
                  "[ERROR]: Epic Games request failed!")

        for i in self.route:

            if self.currentRoute == "":
                """If It's the first iteration, get information from the original JSON file"""

                self.currentRoute = self.rawData[i]

            else:
                """If not, then start digging the dictionaries and lists inside the JSON file"""

                self.currentRoute = self.currentRoute[i]

        self.currentRoute = self.currentRoute[0]  # Gets info from just 1 game

    def process_request(self):
        """Returns the useful information form the request"""

        self.gameData.append(
            self.currentRoute["title"]
        )

        self.gameData.append(
            "https://www.epicgames.com/store/es-ES/product/" +
            self.currentRoute["urlSlug"] +
            "/home"
        )

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

            cache = pointer.execute("SELECT NOMBRE FROM TABLA_1 WHERE ID = (SELECT MAX(ID) FROM TABLA_1)")
            cache = cache.fetchall()

            # If there is no cache or the game is already in the DB then skip...
            try:

                if (cache[0])[0] == self.gameData[0]:  # Compares the last name of the database and the requested
                    return None

            except IndexError:
                print("[ERROR]: Empty database")

            # Adds the register of the game to the DB
            pointer.execute("INSERT INTO TABLA_1 VALUES (NULL,?,?)", self.gameData)

            print(time.strftime('[%Y/%m/%d]' + '[%H:%M]') +
                  "[DB]: New register added:",
                  self.gameData
                  )

            return True

        # Closes connection under any circumstances
        finally:
            conex.commit()  # Saves changes
            conex.close()


obj = Scraping()
