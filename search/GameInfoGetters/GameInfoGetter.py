import abc


#Abstract class to contain a list of riot games api calling methods.
#Known implementing classes: APILeagueGetter, MockLeagueGetter
class GameInfoGetter(abc.ABC):

    @abc.abstractclassmethod
    def getSummonerByName(self, name):
        return NotImplemented

    @abc.abstractclassmethod
    def getMatchlistBySummonerId(self, id, beginIndex, endIndex = None):
        return NotImplemented
    @abc.abstractclassmethod
    def getMatchById(self, id):
        return NotImplemented


