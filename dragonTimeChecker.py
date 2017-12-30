from search.GameInfoGetters.MockInfoGetter import MockInfoGetter
from search.Match.MatchList import MatchList
from search.GameConstants import Dragon
from datetime import timedelta

ml = MatchList(MockInfoGetter(), 'l am eternal', 5)

firstDragons = 0
contestedDragons = 0
backToBackDragons = 0
enemyContestedDragons = 0
enemyBackToBackDragons = 0
firstDragonTimes = []
contestedDragonTimes = []
backToBackDragonTimes = []
enemyContestedDragonTimes = []
enemyBackToBackDragonTimes = []
for dkL in ml.dragonKillList:
    for dk in dkL:
        print(str(dk), end=' ')
    print()


for dkL in ml.dragonKillList:
    i = 0
    while i < len(dkL):
        if dkL[i].type == Dragon.ELDER:
            break
        if dkL[i].thisSummonerKilled:
            if i==0:
                firstDragons+=1
                firstDragonTimes.append(dkL[i].timestamp)
            elif dkL[i-1].thisSummonerKilled:
                backToBackDragons +=1
                backToBackDragonTimes.append(dkL[i].timestamp-dkL[i-1].timestamp)
            else:
                contestedDragons+=1
                contestedDragonTimes.append(dkL[i].timestamp-dkL[i-1].timestamp)
        else:
            if i!=0:
                if dkL[i-1].thisSummonerKilled:
                    enemyContestedDragons+=1
                    enemyContestedDragonTimes.append(dkL[i].timestamp-dkL[i-1].timestamp)
                else:
                    enemyBackToBackDragons+=1
                    enemyBackToBackDragonTimes.append(dkL[i].timestamp-dkL[i-1].timestamp)
        i+=1

print("you get the first dragon on average at " + str(timedelta(milliseconds=sum(firstDragonTimes)/len(firstDragonTimes)).seconds))
print("after you get a dragon, the enemy gets the next dragon " +\
      str(100*enemyContestedDragons/(enemyContestedDragons+backToBackDragons))+\
      "% of the time in average of " + str(timedelta(milliseconds=sum(enemyContestedDragonTimes)/len(enemyContestedDragonTimes)).seconds))
print("after you get a dragon, you get the next dragon " +\
      str(100*backToBackDragons/(enemyContestedDragons+backToBackDragons))+\
      "% of the time in average of " + str(timedelta(milliseconds=sum(backToBackDragonTimes)/len(backToBackDragonTimes)).seconds))
print("after the enemy gets a dragon, the enemy gets the next dragon " +\
      str(100*enemyBackToBackDragons/(enemyBackToBackDragons+contestedDragons))+\
      "% of the time in average of " + str(timedelta(milliseconds=sum(enemyBackToBackDragonTimes)/len(enemyBackToBackDragonTimes)).seconds))
print("after the enemy gets a dragon, you get the next dragon " +\
      str(100*contestedDragons/(enemyBackToBackDragons+contestedDragons))+\
      "% of the time in average of " + str(timedelta(milliseconds=sum(contestedDragonTimes)/len(contestedDragonTimes)).seconds))




