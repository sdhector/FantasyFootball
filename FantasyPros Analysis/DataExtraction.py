## Team Table Function
def TeamInfo():
    """
    Team Info: This function gets the list of teams available at pro-football-reference.com, together with their code and name. 
    
    Parameters: The function takes no parameters. 

    """


    import pandas as pd
    from bs4 import BeautifulSoup
    from selenium import webdriver


    url = "https://www.pro-football-reference.com/"
    driver = webdriver.Chrome()
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    driver.quit()

    TeamTable = pd.DataFrame()
    List = soup.find('div', {'id':'site_menu'}).findChildren('ul')[1].find_all('li')[1].find_all('a')
    for i in List: 
        TeamName = i.get_text()
        TeamCode = i.get('href').split('/')[2]
        TeamTable = TeamTable.append(pd.DataFrame({'TeamName':[TeamName], 'TeamCode':[TeamCode]}))
        
    TeamTable = TeamTable.reset_index().drop('index',axis =1 )
    TeamTable = TeamTable[1:]
    return TeamTable

## Player Archive Data

def PlayerArchive():
    ''' 
    Player Archive: This function gets all the players in pro-football-reference.com

    Parameters: No parameters at the moment. 
    '''
    import pandas as pd
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from string import punctuation 
    import string 

    base_url = "https://www.pro-football-reference.com/players/" # URL to be modified by specifying the first letter of the player's last name to query
    letters = list(string.ascii_uppercase) # list of letters
    Name = [] # initializing a list to store player names
    Position = [] # initializing a list to store player positions
    YearStart = [] # initializing a list to store the player's first year
    YearEnd = [] # initializing a list to store the player's latest or last year. 
    PlayerArchive = pd.DataFrame() # initializing a dataframe to store all data. 

    for l in letters: 
        url = base_url + l + "/" 
        print("working with:" + url)
        driver = webdriver.Chrome()
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        driver.quit()
        List = soup.find('div', {'id':'div_players'}).find_all('p')
        for i in List: 
            Entry = i.get_text()
            Name.append(Entry[0:Entry.find("(")-1])
            Position.append(Entry[Entry.find("(")+1: Entry.find(")")])
            Entry = Entry[Entry.find(")"):]
            YearStart.append( Entry[Entry.find(")"):][Entry.find("-")-4:Entry.find('-')]  )
            YearEnd.append( Entry[Entry.find("-")+1:]  )
        import time
        time.sleep(0) 
        PlayerArchive = PlayerArchive.append(pd.DataFrame({'Name':Name, 'Position':Position, "CareerStart":YearStart, "CareerEnd":YearEnd}))

    #PlayerArchive = pd.DataFrame({'Name':Name, 'Position':Position, "CareerStart":YearStart, "CareerEnd":YearEnd})    
    PlayerArchive = PlayerArchive.drop_duplicates()
    PlayerArchive.Name = PlayerArchive.Name.str.strip(punctuation)
    PlayerArchive.Name = PlayerArchive.Name.str.strip()

    return PlayerArchive


## Roster Data
 
def RosterData(year = 2020):
    """ 
    RosterData: This function gets the roster as currently available in Pro-Football-Reference for the specified year

    Parameters: The year is assumed 2020, so it's optional. 
    """
    import pandas as pd
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from string import punctuation 
    from DataExtraction import TeamInfo


    base_url = "https://www.pro-football-reference.com" 
    year = str(year)
    TeamTable = TeamInfo()
    TeamList = TeamTable.TeamCode.to_list()
    Roster = pd.DataFrame()

    for team in TeamList: 
        url = base_url + "/teams/" + team + "/" + year + "_roster.htm"
        print("Working with: " + url)
        driver = webdriver.Chrome()
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        driver.quit()
        
        TeamName = soup.find('div', {'id':'info'}).find('h1').find_all('span')[1].get_text()
        RosterTable = pd.read_html(page_source)[10].iloc[:,1:4]
        RosterTable['TeamName'] = TeamName
        RosterTable['TeamCode'] = team
        
        url = base_url + "/teams/" + team + "/" + year + "_draft.htm"
        print("Working with: " + url)
        driver = webdriver.Chrome()
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        driver.quit()
        
        TeamName = soup.find('div', {'id':'info'}).find('h1').find_all('span')[1].get_text()
        Draftees = pd.read_html(page_source)[10]
        Draftees = Draftees.iloc[:,1:4]
        Draftees.columns = Draftees.columns.to_frame().iloc[:,1].to_list()
        Draftees['TeamName'] = TeamName
        Draftees['TeamCode'] = team
        
        RosterTable = RosterTable.merge(Draftees, how = 'outer')
        Roster = Roster.append(RosterTable)
        
        import time
        time.sleep(0) 
        
    Roster.Pos = Roster.Pos.str.upper()
    Roster.Player = Roster.Player.str.strip(punctuation)
    Roster = Roster[~Roster.Player.str.contains("Total")]

    return Roster


## Player Data

def PlayerData(year = 2019):
    """
    PlayerData: This function gets the total stats for all players. It also gets the full team data

    Parameters: The assumed year is 2019, but further years might be possible. 
    """

    import pandas as pd
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from string import punctuation 
    from DataExtraction import TeamInfo


    base_url = "https://www.pro-football-reference.com" 
    year = '2019'
    TeamTable = TeamInfo()

    TeamList = TeamTable.TeamCode.to_list()
        
    TeamData = pd.DataFrame()
    PlayerData = pd.DataFrame()

    for team in TeamList: 
        url = base_url + "/teams/" + team + "/" + year + ".htm"
        print("Working with: "+team)
        driver = webdriver.Chrome()
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        driver.quit()
        
        TeamName = soup.find('div', {'id':'info'}).find('h1').find_all('span')[1].get_text()
        TeamStats = pd.read_html(page_source)[10]
        columns = TeamStats.columns.to_frame()
        Filter = (columns.loc[:,0].str.contains("Rushing")) | (columns.loc[:,0].str.contains("Passing"))
        columns.loc[Filter,1] = columns[Filter].loc[:,0] + "_" +columns[Filter].loc[:,1]
        NewColumns = columns.loc[:,1].to_list()
        TeamStats.columns = NewColumns
        TeamStats = TeamStats.rename(columns = {'Player':'TeamName'})
        TeamStats.loc[TeamStats.TeamName == 'Team Stats','TeamName'] = TeamName
        TeamStats = TeamStats[TeamStats['TeamName'] == TeamName]
        TeamStats['TeamCode'] = team
        TeamData = TeamData.append(TeamStats)
        
        Passing = pd.read_html(page_source)[13]
        Rushing_Receiving = pd.read_html(page_source)[14]
        columns = Rushing_Receiving.columns.to_frame()
        Filter = (columns.loc[:,0].str.contains("Rushing")) | (columns.loc[:,0].str.contains("Receiving"))
        columns.loc[Filter,1] = columns[Filter].loc[:,0] + "_" +columns[Filter].loc[:,1]
        NewColumns = columns.loc[:,1].to_list()
        Rushing_Receiving.columns = NewColumns
        PlayerStats = Passing.merge(Rushing_Receiving, how = 'outer')
        PlayerStats['TeamName'] = TeamName
        PlayerStats['TeamCode'] = team

        PlayerData = PlayerData.append(PlayerStats)
        
        import time
        time.sleep(0) 
    PlayerData.Pos = PlayerData.Pos.str.upper()
    PlayerData.Player = PlayerData.Player.str.strip(punctuation)
    PlayerData = PlayerData[~PlayerData.Player.str.contains("Total")]
    return PlayerData, TeamData