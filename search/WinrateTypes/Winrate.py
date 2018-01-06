class Winrate():
    played = 0
    won = 0
    pct = 0
    def __init__(self, gamesPlayed, gamesWon):
        self.played = gamesPlayed
        self.won = gamesWon
        self.pct = float('nan') if self.played == 0 else self.won/self.played

    def __str__(self):
        return '%.2f' % self.won/self.played * 100 + '% winrate over ' + str(self.played) + ' games.' 