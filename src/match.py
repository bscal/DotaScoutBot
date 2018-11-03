from teamfight import Teamfight, TMFPlayer
import gold

class MatchPlayer:
	def __init__(self, data):
		self.slot = 		data["player_slot"]
		self.heroid = 		data["hero_id"]
		isAvaiable = 		"personaname" in data
		self.name = 		data["personaname"] if isAvaiable else "Anonymous"
		self.id = 			data["account_id"]

		self.kda = 			(data["kills"], data["deaths"], data["assists"])
		self.damage = 		data["hero_damage"]
		self.healing = 		data["hero_healing"]
		self.tower = 		data["tower_damage"]
		self.stun = 		data["stuns"]
		self.gpm = 			data["gold_per_min"]
		self.xpm = 			data["xp_per_min"]
		self.gold = 		data["gold"]
		self.net_gold = 	data["total_gold"]
		self.cs = 			data ["last_hits"]
		self.gold_score =	gold.get_gold_score(data["gold_t"][9])

class Match:
	"""Used to hold basic data of a dota match"""

	matchid = 0
	players = []
	teamfights = []

	def __init__(self, match_index: int):
		self.index = match_index
		self.fullParse = False
		self.duration = 0
		self.r_score = 0
		self.d_score = 0

	def on_match(self, data: dict) -> int:
		for player in data["players"]:
			self.players.append(MatchPlayer(player))

		for teamfight in data["teamfights"]:
			count = 0
			tf = Teamfight()

			for player in teamfight["players"]:
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

				if p.damage and p.gold_delta > 0:
					p.was_in = True

				count += 1

			self.teamfights.append(tf)
		return 0

	def on_match_finish(self):
		print("~~~~~ Match {0} Finished ~~~~~".format(self.matchid))
		for player in self.players:
			print("+~~~~~ Match {0} Results ~~~~~+".format(self.index))
			print("Player: {0}".format(player.name))
			print("Hero: {0}".format(player.heroid))
			print("{0}%".format(player.gold_score))
			print("+~~~~~~~~~~~~~~~~~~~~~~~~~~~+")

	def on_finish(self):
		pass