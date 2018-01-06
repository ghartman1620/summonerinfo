from django import template
from math import floor

register = template.Library()

#returns the appropriate string of format 'num% of towerLane towerType towers at min:second'
#deprecated - use towerPct, towerMin, and towerSec to allow the HTML to do string formatting
@register.simple_tag
def tower(towerDict, towerType, towerLane):

    return '%.2f' % towerDict[(towerType, towerLane)][0] + '% of ' + towerLane + ' ' + towerType + ' towers at ' \
        + str(floor(towerDict[(towerType, towerLane)][1].seconds/60)) + ':' + '%.2d' % (towerDict[(towerType, towerLane)][1].seconds%60)
    
@register.simple_tag
def towerSec(towerDict, towerType, towerLane):
    return towerDict[(towerType, towerLane)][1].seconds%60
@register.simple_tag
def towerMin(towerDict, towerType, towerLane):
    return floor(towerDict[(towerType, towerLane)][1].seconds/60)
@register.simple_tag
def towerPct(towerDict, towerType, towerLane):
    return round(towerDict[(towerType, towerLane)][0]*100)/100

@register.simple_tag
def enemyTowerIcon(towerDict, towerType, towerLane):
    #100/4 + 1 is 5 but there is no enemyturret5
    if towerDict[(towerType, towerLane)][0] == 100.0:
        return 'enemyturret4'
    return 'enemyturret' + str(1+floor((towerDict[(towerType, towerLane)][0])/25))
@register.simple_tag
def allyTowerIcon(towerDict, towerType, towerLane):
    #100/4 + 1 is 5, but there is no allyturret5 so we do tihs
    if towerDict[(towerType, towerLane)][0] == 100.0:
        return 'allyturret4'
    return 'allyturret' + str(1+floor((towerDict[(towerType, towerLane)][0])/25))

@register.simple_tag()
def orderWord(num):
    if num==1:
        return 'first'
    if num==2:
        return 'second'
    if num==3:
        return 'third'
    if num==4:
        return 'fourth'
    if num==5:
        return 'fifth'
    if num==6:
        return 'sixth'
    if num==7:
        return 'seventh'


                    