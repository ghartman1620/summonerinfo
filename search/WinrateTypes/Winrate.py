class Winrate():
    played = 0
    won = 0
    def __init__(self, gamesPlayed, gamesWon):
        self.played = gamesPlayed
        self.won = gamesWon
    def __str__(self):
        return '%.2f' % self.won/self.played * 100 + '% winrate over ' + str(self.played) + ' games.' 