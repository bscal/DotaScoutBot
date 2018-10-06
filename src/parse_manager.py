from player import Player
from match import Match
from urllib.request import urlopen
from urllib.error import HTTPError
import json


API_URL = "https://api.opendota.com/api/"
MATCH_URL = API_URL + "matches/"  # + matchid/(params)
PLAYER_URL = API_URL + "players/"  # + steamid/(params)
NUM_OF_GAMES = 5
REQUESTS_PER_SECOND = 1


class ParseManager:
	def __init__(self, type: str = "player"):
		self.type = type
		self.done = False
		self.request_queue = []
		self.open_list = []
		self.closed_list = []
		self.request_count = 0

		self.players = []
		self.matches = []
		self.index = 0

	def prepare_parse(self, parseType, ids):
		# Sets Parsetype
		if parseType == 1:
			self.type == "player"
		elif parseType == 2:
			self.type == "match"

		# Sets up lists of Opendota urls and openlist
		if self.type == "player":
			self.create_player_task(ids)
		elif self.type == "match":
			self.create_match_task(ids)

	def update(self):
		if len(self.request_queue) > 0:
			if self.request_count > (REQUESTS_PER_SECOND - 1):
				return
			else:
				self.make_request()
		elif len(self.open_list) < 1:
			self.finished()

	def make_request(self):
		self.request_count += 1
		try:
			url = self.request_queue[0]
			print(url)

			response = urlopen(url)
			j = response.read()
			data = json.loads(j)

			self.handle_response(url, data)

			self.request_queue.pop(0)
		except HTTPError as err:
			print("Err: 1", err)

	def handle_response(self, url, data):
		# Win/Loss
		if "wl" in url:
			self.players[0].on_wl(data)
		# Parse Matches
		elif "api/matches" in url:
			if self.type == "match":
				self.matches[len(self.closed_list)].on_match(data)
				self.matches[len(self.closed_list)].on_match_finish()
				self.on_input_finished()
			else:
				self.players[0].on_match(data, self.index)
				self.reset_index()
		# Recent Matches List
		elif "matches" in url:
			for match in data:
				self.request_queue.append(MATCH_URL + str(match['match_id']))
		# Players
		elif "players" in url:
			self.players[0].on_player_data(data)
		# Update Heroes
		# TODO
		elif "heroes" in url:
			pass
		else:
			print("Error: Not a proper response.")

	def on_input_finished(self):
		if len(self.open_list) > 0:
			self.closed_list.append(self.open_list.pop(0))

	# Called when parse is FULLY finished.
	def finished(self):
		if len(self.matches) < 1 or len(self.players) < 1:
			pass
		elif self.type == "match":
			self.matches[0].on_finish()
		else:
			self.players[0].on_finish()
		self.done = True
		print("cleaning up...")

	def create_match_task(self, matchids):
		if isinstance(matchids, list):
			for id in matchids:
				self.open_list.append(id)
				self.matches.append(Match(len(self.open_list)))
				self.request_queue.append("{0}{1}".format(MATCH_URL, id))

		else:
			self.open_list.append(matchids)
			self.matches.append(Match(len(self.open_list)))
			self.request_queue.append("{0}{1}".format(MATCH_URL, matchids))

	def create_player_task(self, steamids):
		if isinstance(steamids, list):
			for id in steamids:
				self.open_list.append(id)
				self.players.append(Player(id))
				self.player_request(id)

		else:
			self.open_list.append(steamids)
			self.players.append(Player(steamids))
			self.player_request(steamids)

	def reset_index(self):
		self.index += 1
		if self.index > NUM_OF_GAMES - 1:
			# This resets the matchs for Players
			# Since we dont want to `pop()` the player
			# Everytime a match is returned.
			self.on_input_finished()
			self.index = 0

	def player_request(self, id):
		self.request_queue.append("{0}{1}".format(PLAYER_URL, id))
		self.request_queue.append("{0}{1}/wl?limit={2}".format(PLAYER_URL, id, NUM_OF_GAMES))
		self.request_queue.append("{0}{1}/matches?limit={2}".format(PLAYER_URL, id, NUM_OF_GAMES))
