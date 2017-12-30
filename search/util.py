from datetime import timedelta
class DragonKill():
    thisSummonerKilled = False
    type = None
    timestamp = 0
    def __init__(self, thisSumm, t, ts):
        self.thisSummonerKilled = thisSumm
        self.type= t
        self.timestamp = ts
    def __str__(self):
        return ('This summoner killed ' if self.thisSummonerKilled else \
                 'The enemy team killed ') + str(self.type)\
                 + ' at ' + str(timedelta(milliseconds=self.timestamp))
    def __eq__(self, other):
        return self.thisSummonerKilled == other.thisSummonerKilled and \
               self.type == other.type and \
               self.timestamp == other.timestamp