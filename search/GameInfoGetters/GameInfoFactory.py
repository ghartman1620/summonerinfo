from search.GameInfoGetters.MockInfoGetter import MockInfoGetter
from search.GameInfoGetters.APIInfoGetter import APIInfoGetter
from search.GameInfoGetters.DBAPIInfoGetter import DBAPIInfoGetter


def getInfoGetter(debug=False, dbBad=False):
    if(debug):
        return MockInfoGetter()
    if(dbBad):
        return APIInfoGetter()
    return DBAPIInfoGetter()