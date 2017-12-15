'''
Created on Dec 5, 2017

@author: ghart
'''
'''
interesting dragons information
how much you kill each dragon
how much time you leave each dragon up for when you take the next
how much time the enemy leaves each dragon up for when they take next
% you get each dragon
% you get the first dragon
% you get the first elder dragon
what time you get the first dragon on average
what time the enemy gets the first dragon from you on average

this class makes references to a K/T ratio - killed dragons vs total dragons
'''
class DragonStats():
    percentOfAllElementalDragonsKilledByThisSummoner = 0
    percentOfAllElderDragonsKilledByThisSummoner = 0
    percentOfTotalDragonsKilledByThisSummonerOfEachType = dict()
    percentOfDragonsOfEachTypeKilledByThisSummoner = dict()
    percentOfDragonsKilledByThisSummonerByOrder = dict()
    percentOfElderDragonsByOrder = dict()
    avgTimeAfterRespawnElementalKilledByThisSummonerByType = dict()
    avgTimeAfterRespawnElderKilledByThisSummoner = 0
    avgTimeAfterRespawnElementalKilledByEnemyByType = dict()
    avgTimeAfterRespawnElderKilledByEnemey = 0
    avgTimeFirstDragon = 0
    avgTimeLostFirstDragon =0
    avgTimeFirstElder = 0
    avgTimeLostFirstElder = 0