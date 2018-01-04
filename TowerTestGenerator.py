from search.GameInfoGetters.MockInfoGetter import MockInfoGetter
from search.Match.MatchList import MatchList
from datetime import timedelta
from math import floor

def insertTKIntoDict(d, event):
    if (event['towerType'], event['laneType']) in d:
        d[(event['towerType'], event['laneType'])][0]+=1
        d[(event['towerType'], event['laneType'])][1].append(event['timestamp'])
    else:
        d[(event['towerType'], event['laneType'])] = [1, [event['timestamp']]]
def changeTimeListsToAverageTimes(d, numGames):
    for k in d.keys():
        #d[k][1] = timedelta(milliseconds=sum(d[k][1])/len(d[k][1]))
        if k[0] == 'NEXUS_TURRET':
            d[k] = (100*d[k][0]/numGames/2, timedelta(milliseconds=sum(d[k][1])/len(d[k][1])))
        else:
            d[k] = (100*d[k][0]/numGames,  timedelta(milliseconds=sum(d[k][1])/len(d[k][1])))
def printDict(d):
    for k,v in d.items():
        print('\t\tself.assertEqual(result['+str(k)+'][1].seconds,' + str(v[1].seconds)+')')
        print('\t\tself.assertEqual(result['+str(k)+'][0],'+ str(v[0]) + ')')
ml = MatchList(MockInfoGetter(), 'l am eternal', 5)

wins = 0
losses = 0
towers = [
    ('OUTER_TURRET', 'MID_LANE'),
    ('OUTER_TURRET', 'BOT_LANE'),
    ('OUTER_TURRET', 'TOP_LANE'),
    ('INNER_TURRET', 'MID_LANE'),
    ('INNER_TURRET', 'BOT_LANE'),
    ('INNER_TURRET', 'TOP_LANE'),
    ('BASE_TURRET', 'MID_LANE'),
    ('BASE_TURRET', 'BOT_LANE'),
    ('BASE_TURRET', 'TOP_LANE'),
    ('NEXUS_TURRET', 'MID_LANE')
]

towerKillWinDict = dict()
towerDestroyedWinDict = dict()
towerKillLossDict = dict()
towerDestroyedLossDict = dict()
for match in ml.matches:
    if match.isWin():
        wins+=1
    else:
        losses+=1
    for frame in match.timeline['frames']:
        if match.isWin():
            for event in frame['events']:
                if event['type'] == 'BUILDING_KILL' and event['buildingType'] == 'TOWER_BUILDING':
                    if event['teamId'] == match.teamid:
                        insertTKIntoDict(towerDestroyedWinDict, event)
                    else:
                        insertTKIntoDict(towerKillWinDict, event)
        else:
            for event in frame['events']:
                if event['type'] == 'BUILDING_KILL' and event['buildingType'] == 'TOWER_BUILDING':
                    if event['teamId'] == match.teamid:
                        insertTKIntoDict(towerDestroyedLossDict, event)
                    else:
                        insertTKIntoDict(towerKillLossDict, event)
for k in towers:
    if not k in towerKillWinDict:
       towerKillWinDict[k] = [0, [0]]
    if not k in towerKillLossDict:
       towerKillLossDict[k] = [0, [0]]
    if not k in towerDestroyedWinDict:
        towerDestroyedWinDict[k] = [0, [0]]
    if not k in towerDestroyedLossDict:
        towerDestroyedLossDict[k] = [0, [0]]
    
changeTimeListsToAverageTimes(towerKillLossDict, losses)
changeTimeListsToAverageTimes(towerKillWinDict, wins)
changeTimeListsToAverageTimes(towerDestroyedLossDict, losses)
changeTimeListsToAverageTimes(towerDestroyedWinDict, wins)


print('wins: ' + str(wins))
print('losses: ' + str(losses))
print('tower kills in losses:')
printDict(towerKillLossDict)
print('tower kills in wins:')
printDict(towerKillWinDict)
print('towers lost in losses:')
printDict(towerDestroyedLossDict)
print('towers lost in wins:')
printDict(towerDestroyedWinDict)

