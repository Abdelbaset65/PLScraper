from ast import In
from lxml import html
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

def get_clubs_data():
    html_text = requests.get('https://www.premierleague.com/clubs/').text
    soup = BeautifulSoup(html_text, 'lxml')
    clubs = soup.find_all('div', class_='indexSection')
    clubs = BeautifulSoup(str(clubs), 'lxml')
    clubNames = clubs.find_all('h4', class_='clubName')
    clubNames = [clubName.text for clubName in clubNames]
    Stadiums = clubs.find_all('div', class_='stadiumName')
    Stadiums = [Stadium.text for Stadium in Stadiums]
    Websites = clubs.find_all('a')
    Websites = ["https://www.premierleague.com" + Website["href"]
                for Website in Websites]

    club_df = pd.DataFrame({'Club':clubNames, 'Stadium':Stadiums, 'Website':Websites})
    club_df.to_csv('clubs.csv', index=False)
    print("Clubs data saved to clubs.csv")
    
    stadiumLinks = [Website.replace("overview", "stadium") for Website in Websites]
    stadiumCapacities = []
    stadiumAddresses = []
    stadiumPitchSizes = []
    stadiumRPLAttendances = []
    stadiumBuildDates = []

    for i in range(0, 20):
        # Get the stadium page
        stadiumPage = requests.get(stadiumLinks[i])
        stadiumTree = html.fromstring(stadiumPage.content)

        # Get the stadium capacity
        stadiumCapacity = stadiumTree.cssselect('p:nth-child(1)')[0].text_content()
        stadiumCapacity = stadiumCapacity[-6:]
        stadiumCapacities.append(stadiumCapacity)

        # Get the stadium address, pitch size, RPL attendance and build date
        stadiumRPLAttendance = "Unknown"
        if i == 14:
            stadiumLocation = stadiumTree.cssselect(
                'p:nth-child(6)')[0].text_content()
            stadiumPitchSize = stadiumTree.cssselect(
                'p:nth-child(5)')[1].text_content()
            stadiumBuildDate = stadiumTree.cssselect(
                'p:nth-child(3)')[1].text_content()
        elif i in [3, 15]:
            stadiumLocation = stadiumTree.cssselect(
                'p:nth-child(4)')[1].text_content()
            stadiumPitchSize = stadiumTree.cssselect(
                'p:nth-child(3)')[0].text_content()
            stadiumBuildDate = stadiumTree.cssselect(
                'p:nth-child(2)')[0].text_content()
        elif i in [2, 8, 9, 17]:
            stadiumLocation = stadiumTree.cssselect(
                'p:nth-child(4)')[1].text_content()
            stadiumPitchSize = stadiumTree.cssselect(
                'p:nth-child(3)')[1].text_content()
            stadiumBuildDate = stadiumTree.cssselect(
                'p:nth-child(2)')[0].text_content()
        else:
            stadiumLocation = stadiumTree.cssselect(
                'p:nth-child(5)')[1].text_content()
            stadiumPitchSize = stadiumTree.cssselect(
                'p:nth-child(4)')[1].text_content()
            stadiumRPLAttendance = stadiumTree.cssselect(
                'p:nth-child(2)')[0].text_content()
            stadiumBuildDate = stadiumTree.cssselect(
                'p:nth-child(3)')[1].text_content()

        stadiumAddresses.append(stadiumLocation[17:])
        stadiumPitchSizes.append(stadiumPitchSize[12:])
        if (stadiumRPLAttendance != "Unknown"):
            stadiumRPLAttendances.append(stadiumRPLAttendance[22:])
        else:
            stadiumRPLAttendances.append(stadiumRPLAttendance)
        stadiumBuildDates.append(stadiumBuildDate[-4:])

    # Create a dataframe to store the data
    stadium_df = pd.DataFrame({'Stadium': Stadiums,
                    'Capacity': stadiumCapacities,
                    'Address': stadiumAddresses,
                    'Pitch Size': stadiumPitchSizes,
                    'RPL Attendance': stadiumRPLAttendances,
                    'Build Date': stadiumBuildDates})

    # Save the dataframe to a csv file
    stadium_df.to_csv('stadiums.csv', index=False, encoding='utf-8')
    print("Stadiums data saved to stadiums.csv")

def get_players_data():
    html_text = requests.get('https://www.premierleague.com/clubs/').text
    soup = BeautifulSoup(html_text, 'lxml')
    clubs = soup.find_all('div', class_='indexSection')
    clubs = BeautifulSoup(str(clubs), 'lxml')
    Websites = clubs.find_all('a')
    Websites = ["https://www.premierleague.com" + Website["href"]
                for Website in Websites]
    teamLinks = [Website.replace("overview", "squad") for Website in Websites]

    #Create empty lists for player
    playerLink1 = []
    playerCountries = []
    playerPositions = []

    #For each team link page...
    for i in range(len(teamLinks)):

        #...Download the team page and process the html code...
        squadPage = requests.get(teamLinks[i])
        squadTree = html.fromstring(squadPage.content)

        #...Extract the player links...
        playerLocation = squadTree.cssselect('.playerOverviewCard')
        playerCountry = squadTree.cssselect('.playerCountry')
        playerPosition = squadTree.cssselect('.position')
        #...For each player link within the team page...
        for i in range(len(playerLocation)):

            #...Save the link, complete with domain...
            playerLink1.append("http://www.premierleague.com/" +
                            playerLocation[i].attrib['href'])
            playerCountries.append(playerCountry[i].text_content())
            playerPositions.append(playerPosition[i].text_content())

    # Create lists for each variable
    Name = []
    Team = []
    Age = []
    HeightCM = []
    WeightKG = []
    df = pd.DataFrame(
        {
            'Player':[],
            'Season':[],
            'Team':[]
        }
    )
    df.to_csv('player_career.csv', index=False)
    #Populate lists with each player

    #For each player...
    for i in range(len(playerLink1)):

        #...download and process the two pages collected earlier...
        playerPage1 = requests.get(playerLink1[i])
        playerTree1 = html.fromstring(playerPage1.content)

        #...find the relevant datapoint for each player, starting with name...
        tempName = str(playerTree1.cssselect('div.name')[0].text_content())  
        
        tempSeasons = playerTree1.cssselect('.season p')
        tempTeams = playerTree1.cssselect('span.long')
        Season = []
        prevTeam = []
        if len(tempSeasons) > 5:
            s = 5
        else:
            s = len(tempSeasons)
            
        for i in range(s):
            Season.append(str(tempSeasons[i].text_content()))
        for i in range(s):
            prevTeam.append(str(tempTeams[i].text_content()))
            
        df = pd.DataFrame({
            'Player': tempName,
            'Season': Season,
            'Team': prevTeam
        })
        df.to_csv('player_career.csv', index=False, mode='a', header=False)
        
        #...and team, but if there isn't a team, return "BLANK"...
        try:
            tempTeam = str(playerTree1.cssselect(
                '.table:nth-child(1) .long')[0].text_content())
        except IndexError:
            tempTeam = str("NULL")

        #...and age, but if this isn't there, leave a blank 'no number' number...
        try:
            tempAge = str(playerTree1.cssselect(
                '.pdcol2 li:nth-child(1) .info')[0].text_content())
        except IndexError:
            tempAge = '0'

        #...and height. Needs tidying again...
        try:
            tempHeight = playerTree1.cssselect(
                '.pdcol3 li:nth-child(1) .info')[0].text_content()
            tempHeight = int(re.search(r'\d+', tempHeight).group())
        except IndexError:
            tempHeight = '0'

        #...and weight. Same with tidying and returning blanks if it isn't there
        try:
            tempWeight = playerTree1.cssselect(
                '.pdcol3 li+ li .info')[0].text_content()
            tempWeight = int(re.search(r'\d+', tempWeight).group())
        except IndexError:
            tempWeight = '0'

        #Now that we have a player's full details - add them all to the lists
        Name.append(tempName)
        Team.append(tempTeam)
        Age.append(tempAge.strip())
        HeightCM.append(tempHeight)
        WeightKG.append(tempWeight)

    #Create data frame from lists
    player_df = pd.DataFrame(
        {'Team': Team,
        'Name': Name,
        'Position': playerPositions,
        'Nationality': playerCountries,
        'Age': Age,
        'HeightCM': HeightCM,
        'WeightKG': WeightKG})

    player_df.to_csv('players.csv', index=False)
    print("Players data saved to players.csv")



def get_matches_data():
    # Here I will use a different website to scrape the data for the matches

    fbref = 'https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures'
    page = requests.get(fbref)
    tree = html.fromstring(page.content)
    matchReports = tree.cssselect('.left~ .left+ .left a')

    matchDate = []
    matchSeason = '2022/2023'
    matchResult = []
    matchStadium = []
    hTeam = []
    aTeam = []
    hPossession = []
    aPossession = []
    hGoals = []
    aGoals = []
    hFouls = []
    aFouls = []
    hShots = []
    aShots = []
    hYCards = []
    aYCards = []
    hRCards = []
    aRCards = []

    for i in range(len(matchReports)):
        link = matchReports[i].attrib['href']
        if 'stathead' in link:
            continue
        
        reportPage = requests.get('https://fbref.com' + link)
        reportTree = html.fromstring(reportPage.content)

        tempTeams = reportTree.cssselect('.logo+ strong a')
        tempHTeam = tempTeams[0].text_content()
        tempATeam = tempTeams[1].text_content()
        
        tempStadium = reportTree.cssselect('div:nth-child(6) strong+ small')[0].text_content()
        tempDate = reportTree.cssselect('.scorebox_meta strong a')[0].text_content()
        
        tempResult = reportTree.cssselect('.score')
        tempHGoals = int(tempResult[0].text_content())
        tempAGoals = int(tempResult[1].text_content())
        tempResult = str(tempHGoals) + ' : ' + str(tempAGoals)
        
        tempPossession = reportTree.cssselect('tr:nth-child(3) strong')
        tempHPossession = tempPossession[0].text_content()
        tempAPossession = tempPossession[1].text_content()

        tempShots = reportTree.cssselect('tr:nth-child(7) td > div > div:nth-child(1)')
        tempHShots = tempShots[0].text_content()
        tempAShots = tempShots[1].text_content()
        if tempHShots[-2] == '0':
            if tempHShots[-3] == '0':
                tempHShots = int(tempHShots[-9:-7].strip())
            else:   
                tempHShots = int(tempHShots[-7:-5].strip())
        else:
            tempHShots = int(tempHShots[-8:-6].strip())
        tempAShots = int(tempAShots[-2:].strip())

 
        tempFouls = reportTree.cssselect('#team_stats_extra div:nth-child(1) div:nth-child(6) , #team_stats_extra div:nth-child(1) div:nth-child(4)')
        tempHFouls = int(tempFouls[0].text_content())
        tempAFouls = int(tempFouls[1].text_content())
        
        
        tempYCards = reportTree.cssselect('tfoot .right:nth-child(13)')
        tempHYCards = tempYCards[0].text_content()
        tempAYCards = tempYCards[6].text_content()   


        tempRCards = reportTree.cssselect('tfoot .right:nth-child(14)')
        tempHRCards = tempRCards[0].text_content()
        tempARCards = tempRCards[6].text_content()

        
        matchDate.append(tempDate)
        matchStadium.append(tempStadium)
        matchResult.append(tempResult)
        hTeam.append(tempHTeam)
        aTeam.append(tempATeam)
        hPossession.append(tempHPossession)
        aPossession.append(tempAPossession)
        hGoals.append(tempHGoals)
        aGoals.append(tempAGoals)
        hShots.append(tempHShots)
        aShots.append(tempAShots)
        hFouls.append(tempHFouls)
        aFouls.append(tempAFouls)
        hYCards.append(tempHYCards)
        aYCards.append(tempAYCards)
        hRCards.append(tempHRCards)
        aRCards.append(tempARCards)

    match_df = pd.DataFrame({
            "Date": matchDate,
            "Season": matchSeason,
            "Home Team": hTeam,
            "Away Team": aTeam,
            "Stadium": matchStadium,
            "Result": matchResult,
            "Home Goals": hGoals,
            "Away Goals": aGoals,
            "Home Possession": hPossession,
            "Away Possession": aPossession,
            "Home Shots": hShots,
            "Away Shots": aShots,
            "Home Fouls": hFouls,
            "Away Fouls": aFouls,
            "Home Yellow Cards": hYCards,
            "Away Yellow Cards": aYCards,
            "Home Red Cards": hRCards,
            "Away Red Cards": aRCards
        })
    
    match_df.to_csv('matches.csv', index=False)
    print("Matches data saved to matches.csv")

if __name__ == "__main__":
    get_clubs_data()
    get_players_data()
    get_matches_data()