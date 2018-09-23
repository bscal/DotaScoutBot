MELEE_CREEP_WORTH 	= (((35 + 41) / 2) * 3) * 20
RANGED_CREEP_WORTH 	= ((48 + 58) / 2) * 20
SIEGE_CREEP_WORTH 	= ((66 + 80) / 2) * 2
AVG_CAMP_WORTH 		= 101 * 5

ESTIMATED_TOTAL = MELEE_CREEP_WORTH + RANGED_CREEP_WORTH + SIEGE_CREEP_WORTH + AVG_CAMP_WORTH


def get_gold_score(networth:int) -> float:
	"""
	Calculates the the gold score of the player at 10 minutes.
	:param networth: The networth of the player at 10 minutes
	:return: The percentage of estimated gold based on 10 minute current
	"""
	return round(100 * (networth / ESTIMATED_TOTAL), 2)
