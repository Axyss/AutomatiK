#  Guide on how to code AutomatiK (v1.2) modules

#  Modules are quite easy to code, however there are some guidelines that must be followed.
#  First we need to create a file on the "modules" folder and name it the next way in lower case: (id)_mod.py
#  The field called "id" represents the short name of our module, It must be unique and we are going to need It later. In this case our id is "example".

#  The second thing to do is to import the class "GenericModule", which provides us an easy way to interact with the database where the games will be stored
#  so they aren't notified more than once.

from core.generic_mod import GenericModule

#  After this, we need to create a class that must be called like the "id" we chose before but with its first letter capitalized, 
#  in this case the file is called "example_mod.py" so we'll call our class "Example", and It must inherit the "GenericModule" class 
#  in order to get all It's methods, which will make this process easier.

class Example(GenericModule):

	#  Then we will elaborate the contructor of the class that must contain the next constant attributes:
	#  self.SERVICE_NAME - This variable will contain the full name of the platform we are providing service of with the module. In this case, we are making a module
	#  for the inexistent "Example Games Store".
	#  self.MODULE_ID - We'll introduce here the same "id" we used before to name the class and the file.
	#  self.AUTHOR - Introuce your name/nickname.

	def __init__(self):

		self.SERVICE_NAME = "Example Games Store"
		self.MODULE_ID = "example"
		self.AUTHOR = "Axyss"

	#  The next two methods are not necessary, they just represent the concept of requesting and cleaning 
	#  the data from the web/API we want to retrieve the game data.

	def make_request(self):
		return raw_data

	def process_request(self, raw_data):
		return processed_data

	#  The last requirement is to create a method named "get_free_games", this method is the one that's going to be called by the bot. 

	def get_free_games(self):
		#  This next line represents getting game data and processing it so its format follows
		#  the next scheme [(name_1, link_1), (name_2, link_2) ... (name_n, link_n)]
		possible_free_games = self.process_request(self.make_request())

		#  Once we have our game data correctly formatted like the scheme above, we'll pass that to the database so we can know
		#  which games of the ones detected have been already announced and which ones not. To do so we'll use the self.check_database method
		#  and pass It some parameters, in the table field we have to write (id)_TABLE , and in processed_data we'll put our formatted data.
		free_games = self.check_database(table="EXAMPLE_TABLE", processed_data=possible_free_games)

		return free_games  #  In last place, we'll return what the self.check_database returned
