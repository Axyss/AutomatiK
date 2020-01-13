import requests
import time
from bs4 import BeautifulSoup


class Check_Updates:

    def __init__(self, link, local_version):

        self.localVersion = str(local_version)
        self.remoteVersion = ""
        self.maxLength = 25  # Maximum amount of numbers that a version can support

        # IMPORTANT: the url must contain a slash at the end
        self.url = link

        self.numberList = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

    def get_remote_version(self):
        """Makes the get() request"""

        try:
            req = requests.get(self.url)  # Gets the HTML code from the web page
        except:
            return False

        soup = BeautifulSoup(req.content, 'html.parser')
        self.remoteVersion = soup.find("span",  # Type of container
                                       {"class": "css-truncate-target"},  # Additional attrs
                                       recursive=True).text  # Parameters of the search

    def convert(self):
        """Converts the complex syntax of a version to an integer"""
        localTemp = ""
        remoteTemp = ""

        for i in self.remoteVersion:

            if i in self.numberList:
                remoteTemp += i
            else:
                continue
        else:

            # Adds "0" as many as needed to reach a length of 25 chars
            remoteTemp += "0" * (self.maxLength - len(remoteTemp))

        for i in self.localVersion:

            if i in self.numberList:
                localTemp += i
            else:
                continue
        else:

            # Adds "0" as many as needed to reach a length of 25 chars
            localTemp += "0" * (self.maxLength - len(localTemp))

        if int(remoteTemp) > int(localTemp):
            # If the number of 25 digits of the remote version is higher, then It is a newer one

            # Announce of a newer version
            print(time.strftime('[%Y/%m/%d]' + '[%H:%M]') +
                  f"[UPDATE]: New update ({self.remoteVersion}) available at "
                  f"{self.url + self.remoteVersion}"
                  )
            return {"remote": int(remoteTemp), "local": int(localTemp)}

    def start_checking(self):
        """It will be necessary to use this method inside a thread"""

        while True:
            self.get_remote_version()
            self.convert()
            time.sleep(172800)  # One check every 48 hours
