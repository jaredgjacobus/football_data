## Ben Kite

import pandas
import requests, bs4
import re

def findTables(url):
    res = requests.get(url)
    comm = re.compile("<!--|-->")    
    soup = bs4.BeautifulSoup(comm.sub("", res.text), 'lxml')
    divs = soup.findAll('div', id = "content")
    divs = divs[0].findAll("div", id=re.compile("^all"))
    ids = []
    for div in divs:
        searchme = str(div.findAll("table"))
        x = searchme[searchme.find("id=") + 3: searchme.find(">")]
        x = x.replace("\"", "")
        if len(x) > 0:
            ids.append(x)
    return(ids)
## For example:
## findTables("http://www.pro-football-reference.com/boxscores/201702050atl.htm")


def pullTable(url, tableID):
    res = requests.get(url)
    ## Work around comments
    comm = re.compile("<!--|-->")    
    soup = bs4.BeautifulSoup(comm.sub("", res.text), 'lxml')
    tables = soup.findAll('table', id = tableID)
    data_rows = tables[0].findAll('tr')
    data_header = tables[0].findAll('thead')   
    data_header = data_header[0].findAll("tr")
    data_header = data_header[0].findAll("th")
    game_data = [[td.getText() for td in data_rows[i].findAll(['th','td'])]
        for i in range(len(data_rows))
        ]
    data = pandas.DataFrame(game_data)
    header = []
    for i in range(len(data.columns)):
        header.append(data_header[i].getText())
    data.columns = header
    data = data.loc[data[header[0]] != header[0]]
    data = data.reset_index(drop = True)
    return(data)
## For example:   
## url = "http://www.pro-football-reference.com/boxscores/201702050atl.htm"
## pullTable(url, "team_stats")


## Finds offensive player data for a given season.
## This one was written with fantasy football GMs in mind.
## stat indicates what statistic is desired.
## the user must specify "passing", "rushing", or "receiving"
## the year indicates the year in which the season of interest started
def seasonFinder (stat, year):
    url = "http://www.pro-football-reference.com/years/" + str(year) + "/" + stat + ".htm"
    if stat == "rushing":
        stat = "rushing_and_receiving"
    dat = pullTable(url, stat)
    dat = dat.reset_index(drop = True)
    names = dat.columns
    for c in range(0, len(names)):
        replacement = []
        if type (dat.loc[0][c]) == str:
            k = names[c]
            for i in range(0, len(dat[k])):
                p = dat.loc[i][c]
                xx = re.sub("[#@*&^%$!+]", "", p)
                xx = xx.replace("\xa0", "_")
                xx = xx.replace(" ", "_")
                replacement.append(xx)
            dat[k] = replacement
    return(dat)
    
seasonFinder("passing", 2016)
## For example:
## tables = ["passing", "rushing", "receiving"]
## years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008,
##          2009, 2010, 2011, 2012, 2013, 2014, 2015]
## for y in years:
##     for t in tables:
##         SeasonFinder(t, y)
    
    
## Finds the play by play table a game with the date and homeTeam provided.
## The date has to be yyyymmdd with a 0 on the end.  
## The reference sites use the trailing 0 incase there are multiple games on the same day (it happens in baseball).
## For the 2017 Superbowl the date of February 5th, 2017 would be 201702050.
## The team is the three letter abbrieviation for the home team in lower case.
def playByPlay (date, homeTeam):
    url = "http://www.pro-football-reference.com/boxscores/" +  str(date) + homeTeam + ".htm"
    dat = pullTable(url, "pbp")
    dat = dat.reset_index(drop = True)
    return(dat)
    
## For example:
## This provides the play by play for the 2017 Superbowl.
## playByPlay("201702050", "atl")

    
