from player import Player
from urllib.request import urlopen
from urllib.error import HTTPError
import json
import sys
import time

UPDATES_PER_SECOND = 10
# Opendota's only allows 1(5) request for free(with key)
REQUESTS_PER_SECOND = 1

idle = True

ids = []
players = []
apiQueue = []
matches = []

requestCount = 0
playerIndex = 0
matchCount = 0


def get_milli_time():
	return int(round(time.time() * 1000))


def update_database():
	apiQueue.append("https://api.opendota.com/api/heroes")


def create_player_task(steamid):
	ids.append(steamid)
	players.append(Player(steamid))


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


def handle_response(url, j):
	global playerIndex
	global matchCount

	if "wl" in url:
		players[playerIndex].on_wl(j['win'], j['lose'])

	elif "api/matches/" in url:
		if matchCount == 1:
			players[playerIndex].on_match_result(j)
			on_finished()
			if len(players) > playerIndex:
				playerIndex += 1
		else:
			if len(players) < playerIndex:
				pass
			else:
				players[playerIndex].on_match_result(j)
		matchCount -= 1

	elif "matches?" in url:
		matchCount = len(j)
		create_match_task(j)

	elif "players/" in url:
		players[playerIndex].name = j['profile']['personaname']
		players[playerIndex].rank = j['rank_tier']

	elif "heroes" in url:
		update_hero_data(j)

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
		print("Err: 1 ")


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

##################################################


for i in range(1, len(sys.argv)):
	#if "-update" in sys.argv:
	#	update_database()
	create_player_task(sys.argv[i])

start = get_milli_time() + 1000 / UPDATES_PER_SECOND
count = 0

try:
	while 1:
		sleepTime = start - get_milli_time()
		if sleepTime < 0:
			count += 1
			update()
			start = get_milli_time() + 1000 / UPDATES_PER_SECOND
			if count > UPDATES_PER_SECOND:
				count = 0
				requestCount = 0

except KeyboardInterrupt:
	print("Exiting...")
	sys.exit()
