import requests
import sqlite3
import time
import json


class Scraping:

    def __init__(self):

        self.baseUrl = "https://www.epicgames.com/store/es-ES/product/"
        self.gameData = []  # Data from free games (name, link)
        self.validGameData = []  # Verified games from the DB method

        self.endpoint = "https://graphql.epicgames.com/graphql"

        self.query = {
            "query": "query searchStoreQuery($allowCountries: String, $category: String, $count: Int, $country: "
                     "String!, $keywords: String, $locale: String, $namespace: String, $sortBy: String, "
                     "$sortDir: String, $start: Int, $tag: String, $withPrice: Boolean = false, $withPromotions: "
                     "Boolean = false) {\n  Catalog {\n    searchStore(allowCountries: $allowCountries, "
                     "category: $category, count: $count, country: $country, keywords: $keywords, locale: $locale, "
                     "namespace: $namespace, sortBy: $sortBy, sortDir: $sortDir, start: $start, tag: $tag) {\n      "
                     "elements {\n        title\n        id\n        namespace\n        description\n        "
                     "effectiveDate\n        keyImages {\n          type\n          url\n        }\n        seller {"
                     "\n          id\n          name\n        }\n        productSlug\n        urlSlug\n        url\n  "
                     "      items {\n          id\n          namespace\n        }\n        customAttributes {\n       "
                     "   key\n          value\n        }\n        categories {\n          path\n        }\n        "
                     "price(country: $country) @include(if: $withPrice) {\n          totalPrice {\n            "
                     "discountPrice\n            originalPrice\n            voucherDiscount\n            discount\n   "
                     "         currencyCode\n            currencyInfo {\n              decimals\n            }\n      "
                     "      fmtPrice(locale: $locale) {\n              originalPrice\n              discountPrice\n   "
                     "           intermediatePrice\n            }\n          }\n          lineOffers {\n            "
                     "appliedRules {\n              id\n              endDate\n              discountSetting {\n      "
                     "          discountType\n              }\n            }\n          }\n        }\n        "
                     "promotions(category: $category) @include(if: $withPromotions) {\n          promotionalOffers {"
                     "\n            promotionalOffers {\n              startDate\n              endDate\n             "
                     " discountSetting {\n                discountType\n                discountPercentage\n          "
                     "    }\n            }\n          }\n          upcomingPromotionalOffers {\n            "
                     "promotionalOffers {\n              startDate\n              endDate\n              "
                     "discountSetting {\n                discountType\n                discountPercentage\n           "
                     "   }\n            }\n          }\n        }\n      }\n      paging {\n        count\n        "
                     "total\n      }\n    }\n  }\n}\n",
            "variables": {"category": "freegames", "sortBy": "effectiveDate", "sortDir": "asc", "count": 1000,
                          "country": "ES", "allowCountries": "ES", "locale": "es-ES", "withPrice": True,
                          "withPromotions": True}}

        self.data = None

    def reset_request(self):

        self.gameData = []
        self.data = None
        self.validGameData = []

    def make_request(self):
        """Makes the request and removes the unnecessary JSON data"""

        self.reset_request()

        try:
            self.data = requests.post(self.endpoint,
                                      headers={"Content-type": "application/json;charset=UTF-8"},
                                      data=json.dumps(self.query))

            self.data = json.loads(self.data.content)  # Bytes to json object

        except:
            print(time.strftime('[%Y/%m/%d]' + '[%H:%M]') +
                  "[ERROR]: Epic Games request failed!")

        # Removes the not relevant information from the JSON object
        self.data = self.data["data"]["Catalog"]["searchStore"]["elements"]

    def process_request(self):  # Filters games that are not free
        """Returns the useful information form the request"""

        for i in self.data:

            originalPrice = i["price"]["totalPrice"]["originalPrice"]
            discountPrice = i["price"]["totalPrice"]["discount"]

            if (originalPrice != discountPrice) or (originalPrice == discountPrice == 0):  # If the game isn't free
                continue

            # Parses relevant data such as name and link and adds It to gameData
            temp = (i["title"], str(self.baseUrl + i["productSlug"]))

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
