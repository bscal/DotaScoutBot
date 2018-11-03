"""
For result us the following strings: "w" for Win, "t" for Ties, and "l" for loses

For TMFPlayer.side use "r" for radiant or "d" for dire

For tf_score in parse_teamfights() dire advantage is represented by - negative integers while radiant is + positive integers
"""
from teamfight import Teamfight, TMFPlayer
from match import Match
import gold

# Constant used in usage algorithms
USAGE_USES_MODIFIER = 5


def avg_usage(scores, num_of_teamfights):
	"""
	Averages the usage scores in scores
	:param scores:
	:param num_of_teamfights:
	:type scores: list[float]
	:type num_of_teamfights: int
	:returns avg_usage: int
	"""
	avg_usg = 0
	for i in scores:
		avg_usg += i

	avg_usg /= num_of_teamfights
	return avg_usg


def calculate_teamfight(team):
	return team.dmg + team.heal + (team.casts * USAGE_USES_MODIFIER)


def calculate_usage(player, team_score, match_score, total_fights):
	player_score = player.damage + player.healing + ((player.item_uses + player.ability_uses) * USAGE_USES_MODIFIER)

	return 100 * (player_score / team_score)


class Player:
	"""
		Used to store data of the Player from the steamid's the user entered.
		This is the where all final values and stats should be stored.
		Most values are stored in lists because they are stored from multiple games.
	"""

	def __init__(self, steamid, totalGames):
		self.steamid = steamid
		self.name = ""
		self.rank = 0
		self.wins = 0
		self.loses = 0

		self.total_matches = totalGames

		self.kills = []
		self.assists = []
		self.deaths = []
		self.hero_dmg = []
		self.hero_heal = []
		self.build_dmg = []
		self.stuns = []
		self.gold = []
		self.in_fight_pm = []
		self.out_fight_pm = []
		self.teamfight_count = []
		self.teamfight_usage = []
		self.gold_score = []
		self.lh_score = []
		self.gpm = []
		self.xpm = []

	def parse_teamfight(self, json, hero_id, match):
		"""
		TODO Cleanup and refactor
		TODO Fix usage percentage
		TODO Simplify any algorithms or calculations

		Mainly setups and stores values for Teamfights that happend in the match.
		Will take the json data and go through each teamfight parsing that data needed.
		All calculations will to passed to calculate_match_results() function for calculations.

		:param json: 		The json data
		:param hero_id: 	The steamid of the main player for the match
		:param match: 		Match data
		"""
		teamfights = []
		heroes = []
		side = ""

		for h in json["players"]:
			heroes.append(h["hero_id"])

		for t in json["teamfights"]:
			count = 0
			tf = Teamfight()

			for player in t["players"]:
				p = TMFPlayer()

				if player["buybacks"] != 0:
					p.buyback = True

				p.deaths = player["deaths"]
				p.damage = player["damage"]
				p.healing = player["healing"]
				p.gold_delta = player["gold_delta"]
				p.xp_delta = player["xp_delta"]

				for v in player["ability_uses"].values():
					p.ability_uses += v
				for v in player["item_uses"].values():
					p.item_uses += v
				for v in player["killed"].values():
					p.kills += v

				if count < 5:
					p.side = "r"
					tf.radiant_team.dmg += p.damage
					tf.radiant_team.heal += p.healing
					tf.radiant_team.casts += (p.ability_uses + p.item_uses)
					tf.radiant_team.kills += p.kills
				else:
					p.side = "d"
					tf.dire_team.dmg += p.damage
					tf.dire_team.heal += p.healing
					tf.dire_team.casts += (p.ability_uses + p.item_uses)
					tf.dire_team.kills += p.kills

				p.hero_id = heroes[count]

				count += 1

				if p.damage > 1:
					tf.players.append(p)
					if p.hero_id == hero_id:
						side = p.side
						tf.is_in = True

			teamfights.append(tf)

		self.calculate_match_results(hero_id, match, teamfights, side)

	def calculate_match_results(self, hero_id, match, teamfights, side):
		"""
		Used to calculate data and other statics of teamfights of a given match

		:param hero_id:			The steamid of the main player for the match
		:param match:			Match Data
		:param teamfights:		List of teamfights from match
		:param side:			Side of the main player for the given match
		"""
		# Used to store the scores of all teamfights so they can be condensed into 1 float for whole game
		scores = []
		# In plus minus
		ipm = 0
		# Out plus minus
		opm = 0
		num_of_fights = len(teamfights)
		for tf in teamfights:
			r_gold = 0
			d_gold = 0
			for p in tf.players:
				# Adds up total gold
				team_usage_score = 0
				if p.side == "r":
					r_gold += p.gold_delta
					team = tf.radiant_team
					team_usage_score = calculate_teamfight(team)
				elif p.side == "d":
					d_gold += p.gold_delta
					team = tf.dire_team
					team_usage_score = calculate_teamfight(team)

				# Calculates the usage score for the teamfight
				usage = calculate_usage(p, team_usage_score, match, num_of_fights)

				if p.hero_id == hero_id:
					# print(usage)
					scores.append(usage)

			# Calculates where and what to add/subtract the result of a teamfight
			# Here is how it works:
			# -> Checks which side "Radiant (r)" or "Dire (d)" won that match
			# -> Stores the result in the teamfight object
			# -> Checks if the side of the main Player is r or d
			# -> Checks if the main Player was in or out of the teamfight
			# -> Does the correct operation for the situation
			# -> Repeat for next teamfight
			if r_gold > d_gold:
				tf.result = "r"
				if side == "r":
					if tf.is_in:
						ipm += 1
					else:
						opm += 1
				else:
					if tf.is_in:
						ipm -= 1
					else:
						opm -= 1
			else:
				tf.result = "d"
				if side == "d":
					if tf.is_in:
						ipm += 1
					else:
						opm += 1
				else:
					if tf.is_in:
						ipm -= 1
					else:
						opm -= 1

		# Returns the avg usage rate.
		usg = avg_usage(scores, num_of_fights)

		# Sets final player data
		self.set_teamfight_results(usg, ipm, opm, num_of_fights)

	def set_teamfight_results(self, usg=0, ipm=0, opm=0, num_of_fights=0):
		self.teamfight_usage.append(round(usg, 2))
		self.in_fight_pm.append(ipm)
		self.out_fight_pm.append(opm)
		self.teamfight_count.append(num_of_fights)

	def on_wl(self, data):
		"""On Win Lose is when the api response is the wl of X games"""
		self.wins = data["win"]
		self.loses = data["lose"]

	def on_player_data(self, data):
		self.name = data["profile"]["personaname"]
		self.rank = data["rank_tier"]

	def on_match(self, data, match_index):
		"""When the api response is a dota match"""
		hero_id = 0

		match = Match(match_index)
		match.duration = data["duration"]
		match.d_score = data["dire_score"]
		match.r_score = data["radiant_score"]

		if data["chat"] is None:
			match.fullParse = False
		else:
			match.fullParse = True

		for player in data["players"]:
			if str(player["account_id"]) == self.steamid:
				self.assists.append(player["assists"])
				self.kills.append(player["kills"])
				self.deaths.append(player["deaths"])
				self.hero_dmg.append(player["hero_damage"])
				self.hero_heal.append(player["hero_healing"])
				self.build_dmg.append(player["tower_damage"])
				self.stuns.append(player["stuns"])
				self.gold.append(player["gold"])
				self.gpm.append(player["gold_per_min"])
				self.xpm.append(player["xp_per_min"])

				# Temp variables to handle if the match is unparsed on Opendota
				gold_score = 0
				if match.fullParse is True:
					gold_score = gold.get_gold_score(player["gold_t"][9])
				self.gold_score.append(gold_score)
				hero_id = player["hero_id"]

		if match.fullParse is True:
			self.parse_teamfight(data, hero_id, match)
		else:
			# Sets the teamfight values to defaults (0)
			self.set_teamfight_results()

		self.on_match_finish(match)

	def on_match_finish(self, match):
		print("~ Match {0} Finished ~".format(match.index + 1))
		print("Full Parse:", match.fullParse)
		if match.fullParse is True:
			print("Usage:", self.teamfight_usage[match.index])
			print("GoldScore:", self.gold_score[match.index])

	def on_finish(self):
		"""
			When no there are no longer any user entered Players in the queue on_finish() will be called.
			Usually this is where any final data is created (Averaged of the data mostly).
		"""
		print("")
		print("~~~~~ %s's Stats ~~~~~" % self.name)
		print("Rank:", self.rank)
		print("{0} Total Games".format(self.total_matches))
		print("W/L: {0}%({1}/{2})".format(100 * self.wins / self.total_matches, self.wins, self.loses))

		k = sum(self.kills) / self.total_matches
		d = sum(self.deaths) / self.total_matches
		a = sum(self.assists) / self.total_matches
		print("AVG Kills:", k)
		print("AVG Deaths:", d)
		print("AVG Assists:", a)
		print("AVG KDA:", round((k + a) / d), 2)
		print("AVG GPM:", sum(self.gpm) / self.total_matches)
		print("AVG XPM:", sum(self.xpm) / self.total_matches)

		ipm = sum(self.in_fight_pm)
		opm = sum(self.out_fight_pm)
		total = sum(self.teamfight_count)
		usage = sum(self.teamfight_usage)
		gold_score = sum(self.gold_score)

		print("Teamfight +-: {0}/{1}".format((ipm / self.total_matches), (opm / self.total_matches)))
		print("Usage: {0}%".format(round((usage / self.total_matches), 2)))
		print("Fights per Match {0}".format(total / self.total_matches))
		print("Gold Score: {0}".format(round((gold_score / self.total_matches), 2)))
