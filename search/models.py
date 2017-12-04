from django.db import models

# Create your models here.
class Match(models.Model):
    gameId = models.BigIntegerField(primary_key=True)
    jsonString = models.TextField()
    


''''I started trying to translate the riot games match data into
a database with appropriately named fields.
An easier approach is to just store the json string in the db as above.
Maybe I'll either complete this or delete it in the future. Who knows?
it would be much nicer to the db if i did it this way...
the timelines DEFINITELY have to be like this though
class MatchDto(models.Model):
    seasonId = models.IntegerField()
    queueId = models.IntegerField()
    gameId = models.BigIntegerField(primary_key=True)
    #participantIdentities = List[ParticipantIdentityDto]
    gameVersion = models.CharField(max_length=30)
    platformId = models.CharField(max_length=10)
    gameMode = models.CharField(max_length=30)
    mapId = models.IntegerField()
    gameType = models.CharField(max_length=20)
    #teams = List[TeamStatsDto]
    #participants = List[ParticipantDto]
    gameDuration = models.BigIntegerField()
    gameCreation = models.BigIntegerField()
    
class ParticipantIdentityDto(models.Model):
    match = models.ForeignKey(MatchDto, on_delete=models.CASCADE, related_name='participantIdentities')
    #player = PlayerDto
    participantId = models.IntegerField()
    
    
class PlayerDto(models.Model):
    participantIdentity = models.OneToOneField(ParticipantIdentityDto, primary_key=True,
                                               on_delete=models.CASCADE, related_name='player')
    currentPlatformId = models.CharField(max_length=10)
    summonerName = models.CharField(max_length=16)
    matchHistoryUri = models.CharField(max_length= 50)
    platformId = models.CharField(max_length=10)
    currentAccountId = models.BigIntegerField()
    profileIcon = models.IntegerField()
    summonerId = models.BigIntegerField()
    accountId = models.BigIntegerField()
    
class TeamStatsDto(models.Model):
    match = models.ForeignKey(MatchDto,
                              on_delete= models.CASCADE, related_name='teams')
    firstDragon = models.BooleanField()
    firstInhibitor = models.BooleanField()
    #bans = List[TeamBansDto]
    baronKills = models.IntegerField()
    firstRiftHerald = models.BooleanField()
    firstBaron = models.BooleanField()
    riftHeraldKills = models.IntegerField()
    firstBlood = models.BooleanField()
    teamId = models.IntegerField()
    firstTower = models.
'''