'''
Created on Jan 1, 2018

@author: ghart
'''
from search.GameInfoGetters.MockInfoGetter import MockInfoGetter
from search.Match.MatchList import MatchList
matchlist = MatchList(MockInfoGetter(), 'l am eternal', 5)
for match in matchlist.matches:
    print('new match, l am eternal is on ' + str(match.teamid) + ' win?: ' + str(match.isWin()))
    for tk in match.towers():
        print(str(tk))
        