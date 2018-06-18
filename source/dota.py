from player import Player
from urllib.request import urlopen
from urllib.error import HTTPError
import json
import sys
import time

UPDATES_PER_SECOND = 10
# Opendota's only allows 1(5) request for free(with key)
REQUESTS_PER_SECOND = 1
DEBUG = True

idle = True

ids = []
players = []
apiQueue = []
matches = []

requestCount = 0
playerIndex = 0
matchIndex = 0
matchCount = 0


def get_milli_time():
	return int(round(time.time() * 1000))


def update_database():
	apiQueue.append("https://api.opendota.com/api/heroes")


def add_player(steamid):
	"""
	Appends and prepares the program to scout a player.
	:param steamid: Steamid of player
	"""
	ids.append(steamid)
	players.append(Player(steamid))


def add_match(matchid):
	"""
	Appends and prepares the program to scout a match.
	:param matchids: Matchid of match
	"""
	pass


def add_player_matches(steamid, num_of_matches):
	"""
	:param steamid: Steamid of player
	:param num_of_matches: Number of matches to parse
	"""
	pass


def create_scout_task(steamid):
	apiQueue.append("https://api.opendota.com/api/players/" + steamid)
	apiQueue.append("https://api.opendota.com/api/players/" + steamid + "/wl?limit=5")
	apiQueue.append("https://api.opendota.com/api/players/" + steamid + "/matches?limit=5")


def create_match_task(json_data):
	for match in json_data:
		apiQueue.append("https://api.opendota.com/api/matches/" + str(match['match_id']))


def update_hero_data(j):
	with open("heroes.txt", "w") as file:
		for h in j:
			file.write(str(h["id"]) + " " + h["name"] + " " + h["localized_name"] + "\n")
	print("Heroes File Updated...")


def on_finished():
	global idle
	players[playerIndex].on_finish()
	idle = True


def on_match_result(json_data):
	players[playerIndex].on_match_result(json_data, matchCount - matchIndex)


def handle_response(url, json_data):
	global playerIndex
	global matchIndex
	global matchCount

	if "wl" in url:
		players[playerIndex].on_wl(json_data['win'], json_data['lose'])

	elif "api/matches" in url:
		if matchIndex == 1:
			on_match_result(json_data)
			on_finished()
			if len(players) > playerIndex:
				playerIndex += 1
		else:
			if len(players) < playerIndex:
				pass
			else:
				on_match_result(json_data)
		matchIndex -= 1

	elif "matches?" in url:
		matchIndex = matchCount = len(json_data)
		create_match_task(json_data)

	elif "players" in url:
		players[playerIndex].name = json_data['profile']['personaname']
		players[playerIndex].rank = json_data['rank_tier']

	elif "heroes" in url:
		update_hero_data(json_data)

	else:
		print("Not a proper response")


def make_request():
	global requestCount
	requestCount += 1
	try:
		url = apiQueue[0]

		response = urlopen(url)
		data = response.read()
		j = json.loads(data)

		print(url)

		handle_response(url, j)

		apiQueue.pop(0)
	except HTTPError:
		print("Err: 1")


def process():
	if len(apiQueue) > 0:
		if requestCount > (REQUESTS_PER_SECOND - 1):
			pass
		else:
			make_request()


def update():
	global idle
	if idle and len(ids) > 0:
		create_scout_task(ids[0])
		ids.pop(0)
		idle = False
	else:
		process()

#####################################################
# Main												#
#####################################################


def init_dota(args):
	""" Parses the arguments to setup whatever user needs. """
	mode = "player"
	for i, arg in enumerate(args):
		if i == 0:
			continue
		if "-" in arg:
			if arg == "-match":
				mode = "match"
			elif arg == "-pm":
				add_player_matches(args[2], arg[3])
				break
			elif arg == "-update":
				update_database()
		elif mode == "player":
			add_player(arg)
		elif mode == "match":
			add_match(arg)


def main():
	global requestCount

	start = get_milli_time() + 1000 / UPDATES_PER_SECOND
	count = 0

	init_dota(sys.argv)

	try:
		while 1:
			sleep_time = start - get_milli_time()
			if sleep_time < 0:
				count += 1
				update()
				start = get_milli_time() + 1000 / UPDATES_PER_SECOND
				if count > UPDATES_PER_SECOND:
					count = 0
					requestCount = 0

	except KeyboardInterrupt:
		print("Exiting...")
		sys.exit()


if __name__ == "__main__":
	main()
