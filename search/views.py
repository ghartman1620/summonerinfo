from datetime import datetime, timedelta, time
from django.shortcuts import render, redirect

from search.GameInfoGetters.GameInfoFactory import getInfoGetter
from search.WinrateTypes.Winrate import Winrate
from search.Match.MatchList import MatchList
from search.GameConstants import QueueType


''''
def win(name, match):
    winningTeam = 0 if match['teams'][0]['win'] == 'Win' else 1
    for i in range(0,5):
        if match['participantIdentities'][i]['player']['summonerName'].lower() == name.lower(): #name is on 1st team
            if winningTeam == 0: #and 1st team won
                return True
            else:
                return False
    #if we get here name is on second team
    if winningTeam == 1: #and second team won
        return True
    return False #else player is on second team and first team won
'''
def wrListToStringList(winrates):
    stringList = []
    for wr in winrates:
        stringList.append(str(wr))
    return stringList

HUNDREDS_OF_MATCHES = 1
def search(request, name):
    
    '''gameinfo = getInfoGetter(True)
    print('creating MatchList')
    ml = MatchList(gameinfo, 'l am eternal')
    print("Searching for " + name)
    id = gameinfo.getSummonerByName(name)['accountId']
    matchtimes = []
    allmatches = []
    matchdetails = []
    for i in range(0,HUNDREDS_OF_MATCHES):
        matches = gameinfo.getMatchlistBySummonerId(id, i*100, 50) 
            
        for match in matches['matches']:
            allmatches.append(match)
            matchdetails.append(gameinfo.getMatchById(match['gameId']))
    i = 0
    winrateByTime = [[0 for x in range(2)] for y in range(4)]
    for match in allmatches:
        if match['queue'] == 420:
            #NA: match['timestamp']/1000 IS PST OF BEGINNING OF MATCH
            #VERIFIED 
            utctime = datetime.fromtimestamp(match['timestamp']/1000)
            offset = timedelta(hours=0)
            time = utctime - offset
            matchtimes.append(str(time) + ' timestamp: ' +str(match['timestamp']) + '   '+ str(match['gameId']) + '    ' + str(matchdetails[i]['queueId']) + ' ' + str(win(name, matchdetails[i])))
            
            if win(name, matchdetails[i]):
                if time.hour >= 18:
                    winrateByTime[3][1]+=1
                    winrateByTime[3][0]+=1
                elif time.hour >= 12:
                    winrateByTime[2][1]+=1
                    winrateByTime[2][0]+=1
                elif time.hour >= 6:
                    winrateByTime[1][1]+=1
                    winrateByTime[1][0]+=1
                else: #0-6
                    winrateByTime[0][1]+=1
                    winrateByTime[0][0]+=1
            else:
                if time.hour >= 18:
                    winrateByTime[3][0]+=1
                elif time.hour >= 12:
                    winrateByTime[2][0]+=1
                elif time.hour >= 6:
                    winrateByTime[1][0]+=1
                else: #0-6
                    winrateByTime[0][0]+=1
        i+=1
        
            #print("not a ranked game.")
    onPlayersTeam = dict()
    vsPlayersTeam = dict()
    for match in matchdetails:
        if match['queueId'] == 420:
            thisSummonersTeam = []
            enemyTeam = []
            thisSummonerWon = win(name, match)
            thisSummonerId = 0
            
            thisSummonersTeamId = 0
            for player in match['participantIdentities']:
                if player['player']['summonerName'].lower() == name:
                    thisSummonerId = player['participantId']
                    break
            for participant in match['participants']:
                
                if participant['participantId'] == thisSummonerId:
                    thisSummonersTeamId = participant['teamId']
                    break
            
            participantIds = dict()
            for player in match['participantIdentities']:
                participantIds[player['participantId']] = player['player']['summonerName']
            
            for participant in match['participants']:
                if participant['teamId'] == thisSummonersTeamId:
                    thisSummonersTeam.append(participant['participantId'])
                else:
                    enemyTeam.append(participant['participantId'])
            if thisSummonerWon:
                for particId in thisSummonersTeam:
                    if participantIds[particId] in onPlayersTeam:
                        wg = onPlayersTeam[participantIds[particId]]
                        onPlayersTeam[participantIds[particId]] = (wg[0]+1, wg[1]+1)
                    else:
                        onPlayersTeam[participantIds[particId]] = (1,1)
                for particId in enemyTeam:
                    if participantIds[particId] in vsPlayersTeam:
                        wg = vsPlayersTeam[participantIds[particId]]
                        vsPlayersTeam[participantIds[particId]] = (wg[0], wg[1]+1)
                    else:
                        vsPlayersTeam[participantIds[particId]] = (0,1)
            else:
                for particId in thisSummonersTeam:
                    if participantIds[particId] in onPlayersTeam:
                        wg = onPlayersTeam[participantIds[particId]]
                        onPlayersTeam[participantIds[particId]] = (wg[0], wg[1]+1)
                    else:
                        onPlayersTeam[participantIds[particId]] = (0,1)
                for particId in enemyTeam:
                    if participantIds[particId] in vsPlayersTeam:
                        wg = vsPlayersTeam[participantIds[particId]]
                        vsPlayersTeam[participantIds[particId]] = (wg[0]+1, wg[1]+1)
                    else:
                        vsPlayersTeam[participantIds[particId]] = (1,1)
    onPlayersTeamList = []
    for item in onPlayersTeam.items():
        if item[1][1] > 1:
            onPlayersTeamList.append(item)
    onPlayersTeamList.sort(key=lambda x: x[1][1], reverse=True)

    vsPlayersTeamList = []
    for item in vsPlayersTeam.items():
        if item[1][1] > 1:
            vsPlayersTeamList.append(item)
    vsPlayersTeamList.sort(key=lambda x: x[1][1], reverse=True)
    
    print(onPlayersTeamList)
    print(vsPlayersTeamList)
    
    winratesByTime = []
    if winrateByTime[3][0] != 0:
        winratesByTime.append('18:00-24:00: ' + str(winrateByTime[3][1]/winrateByTime[3][0]*100) + '% of ' + str(winrateByTime[3][0]) + ' games.')
    else:
        winratesByTime.append('18:00-24:00: no games')
    if winrateByTime[2][0] != 0:
        winratesByTime.append('12:00-18:00: ' + str(winrateByTime[2][1]/winrateByTime[2][0]*100) + '% of ' + str(winrateByTime[2][0]) + ' games.')
    else:
        winratesByTime.append('12:00-18:00: no games')
    if winrateByTime[1][0] != 0:
        winratesByTime.append('6:00-12:00: ' + str(winrateByTime[1][1]/winrateByTime[1][0]*100) + '% of ' + str(winrateByTime[1][0]) + ' games.')
    else:
        winratesByTime.append('6:00-12:00: no games')
    if winrateByTime[0][0] != 0:
        winratesByTime.append('0:00-6:00: ' + str(winrateByTime[0][1]/winrateByTime[0][0]*100) + '% of ' + str(winrateByTime[0][0]) + ' games.')
    else: 
        winratesByTime.append('0:00-6:00: no games')
    
    
    print(winratesByTime)
    return render(request, 'search/search.html', {
        'name'           : name             ,  
        'matchtimes'     : matchtimes       , 
        'winratesByTime' : winratesByTime   ,
        'onPlayersTeam'  : onPlayersTeamList,
        'vsPlayersTeam'  : vsPlayersTeamList,
    })
    '''
    gameinfo = getInfoGetter()
    matchList = MatchList(gameinfo, name, queue=QueueType.RANKED_SOLODUO)
    #remember that you wrote the text 'in PST only' into search.html
    return render(request, 'search/search.html', {
        'name'            : name                                                    ,
        'overview'        : str(matchList)                                          ,
        'winratesByTime'  : wrListToStringList(matchList.winrateByTime())           ,
        'otherSummonersWr': wrListToStringList(matchList.winrateByOtherSummoners()) ,
    })
    
def searchtarget(request):
    return redirect('search:search',request.POST['summonerName'])
