"""
For result us the following strings: "w" for Win, "t" for Ties, and "l" for loses

For TMFPlayer.side use "r" for radiant or "d" for dire

For tf_score in parse_teamfights() dire advantage is represented by - negative integers while radiant is + positive integers
"""
from teamfight import Teamfight, TMFPlayer


class Match:
	"""Used to hold basic data of a dota match"""
	def __init__(self):
		self.duration = 0
		self.r_score = 0
		self.d_score = 0


class Player:
	"""
		Used to store data of the Player from the steamid's the user entered.
		This is the where all final values and stats should be stored.
		Most values are stored in lists because they are stored from multiple games.
	"""
	def __init__(self, steamid):
		self.steamid = steamid
		self.name = ""
		self.rank = 0
		self.wins = 0
		self.loses = 0

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
				for k, v in player["ability_uses"].items():
					p.ability_uses += v
				for k, v in player["item_uses"].items():
					p.item_uses += v
				for k, v in player["killed"].items():
					p.kills += v

				if count < 5:
					p.side = "r"
					tf.r_dmg += p.damage
					tf.r_heal += p.healing
					tf.r_casts += (p.ability_uses + p.item_uses)
					tf.r_kills += p.kills
				else:
					p.side = "d"
					tf.r_dmg += p.damage
					tf.r_heal += p.healing
					tf.r_casts += (p.ability_uses + p.item_uses)
					tf.r_kills += p.kills

				p.hero_id = heroes[count]
				if p.hero_id == hero_id:
					side = p.side

				count += 1

				if p.damage < 1:
					tf.is_in = True
					tf.players.append(p)
				else:
					tf.is_in = False

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
		for tf in teamfights:
			r_gold = 0
			d_gold = 0
			for p in tf.players:
				print("ran")
				# Teamfight team gold totals
				if p.side == "r":
					r_gold += p.gold_delta

					# Teamfight Usage Score
					# TODO USAGE BROKEN
					usage = 100 * (((p.damage + 1) * (p.healing + 1) * (p.ability_uses + p.item_uses + 1) * 5 * (
							tf.r_kills + 1 / 5)) / (match.r_score * (tf.r_dmg + 1) * (tf.r_heal + 1) * (
							(tf.r_casts + .1) * 5)))
				else:
					d_gold += p.gold_delta

					# Teamfight Usage Score
					usage = 100 * (((p.damage + 1) * (p.healing + 1) * (p.ability_uses + p.item_uses + 1) * 5 * (
							tf.d_kills + 1 / 5)) / (match.d_score * (tf.d_dmg + 1) * (tf.d_heal + 1) * (
							(tf.d_casts + 1) * 5)))

				if p.hero_id == hero_id:
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

		us = 0
		for i in scores:
			us += i

		us / len(teamfights)

		# Final data
		self.teamfight_usage = us
		self.in_fight_pm.append(ipm)
		self.out_fight_pm.append(opm)
		self.teamfight_count.append(len(teamfights))

		print(ipm)
		print(opm)
		print(len(teamfights))

	def on_wl(self, wins, loses):
		"""On Win Lose is when the api response is the wl of X games"""
		self.wins = wins
		self.loses = loses

	def on_match_result(self, json):
		"""When the api response is a dota match"""
		hero_id = 0

		for player in json["players"]:
			if str(player["account_id"]) == self.steamid:
				self.assists.append(player["assists"])
				self.kills.append(player["hero_kills"])
				self.deaths.append(player["deaths"])
				self.hero_dmg.append(player["hero_damage"])
				self.hero_heal.append(player["hero_healing"])
				self.build_dmg.append(player["tower_damage"])
				self.stuns.append(player["stuns"])
				self.gold.append(player["gold"])
				hero_id = player["hero_id"]

		match = Match()
		match.duration = json["duration"]
		match.d_score = json["dire_score"]
		match.r_score = json["radiant_score"]

		self.parse_teamfight(json, hero_id, match)

	def on_finish(self):
		"""
			When no there are no longer any user entered Players in the queue on_finish() will be called.
			Usually this is where any final data is created (Averaged of the data mostly).
		"""
		total_games = len(self.kills)
		print(self.name + " " + str(self.rank))
		print(str(self.wins) + "/" + str(self.loses))
		tk = 0
		for k in self.kills:
			tk += k
		r = tk / total_games
		print(r)

		ipm = 0
		opm = 0
		total = 0
		for i in range(total_games):
			ipm += self.in_fight_pm[i]
			opm += self.out_fight_pm[i]
			total += self.teamfight_count[i]
		print(ipm / total_games)
		print(opm / total_games)
		print(total / total_games)
