import requests
from bs4 import BeautifulSoup
import lxml
import time

trains_on_lines = {
    "Alamein":["X'Trapolis 100"],
    "Belgrave":["X'Trapolis 100"],
    "Craigieburn":["Alstom Comeng","EDI Comeng","Siemens Nexas"],
    "Cranbourne":["HCMT"],
    "Frankston":["Alstom Comeng","EDI Comeng","Siemens Nexas","X'Trapolis 100"],
    "Glen Waverley":["X'Trapolis 100"],
    "Hurstbridge":["X'Trapolis 100"],
    "Lilydale":["X'Trapolis 100"],
    "Mernda":["X'Trapolis 100"],
    "Pakenham":["HCMT"],
    "Sandringham":["Alstom Comeng","EDI Comeng","Siemens Nexas"],
    "Sunbury":["Alstom Comeng","EDI Comeng","Siemens Nexas","HCMT"],
    "Upfield":["Alstom Comeng","EDI Comeng","Siemens Nexas"],
    "Werribee":["Alstom Comeng","EDI Comeng","Siemens Nexas","X'Trapolis 100"],
    "Williamstown":["Alstom Comeng","EDI Comeng","Siemens Nexas","X'Trapolis 100"]
}
linelist = [
    'Alamein', #1
    'Belgrave', #2
    'Craigieburn', #3
    'Cranbourne', #4
    'Mernda', #5
    'Frankston', #6
    'Glen Waverley', #7
    'Hurstbridge', #8
    'Lilydale', #9
    'Pakenham', #11
    'Sandringham', #12
    'Sunbury', #14
    'Upfield', #15
    'Werribee', #16
    'Williamstown' #17
]

def checkTrainType(number):
    car = str(number).upper()
    try:
        if car.endswith("M"):
            car = car.rstrip(car[-1])
            try:
                car = int(car)
            except:
                return None
            if car >= 561 and car <= 680:
                return "Alstom Comeng"
            elif car >= 301 and car <= 468:
                return "EDI Comeng"
            elif car >= 471 and car <= 554:
                return "EDI Comeng"
            elif car >= 1 and car <= 288:
                return "X'Trapolis 100"
            elif car >= 851 and car <= 986:
                return "X'Trapolis 100"
            elif car >= 701 and car <= 844:
                return "Siemens Nexas"
            else:
                return None
        elif car.endswith("T"):
    
            car = car.rstrip(car[-1])
            try:
                car = int(car)
            except:
                return None
            if car >= 1131 and car <= 1190:
                return "Alstom Comeng"
            elif car >= 1001 and car <= 1084:
                return "EDI Comeng"
            elif car >= 1086 and car <= 1127:
                return "EDI Comeng"
            elif car >= 1301 and car <= 1444:
                return "X'Trapolis 100"
            elif car >= 1626 and car <= 1693:
                return "X'Trapolis 100"
            elif car >= 851 and car <= 986:
                return "X'Trapolis100"
            elif car >= 2501 and car <= 2572:
                return "Siemens Nexas"
            else:
                return None
        else:
            try:
                car = int(car)
            except:
                return None
            
            if car >= 9001 and int(car) <= 9070 or int(car) >= 9101 and int(car) <= 9170 or int(car) >= 9201 and int(car) <= 9270 or int(car) >= 9301 and int(car) <= 9370 or int(car) >= 9701 and int(car) <= 9770 or int(car) >= 9801 and int(car) <= 9870 or int(car) >= 9901 and int(car) <= 9970:
                return "HCMT"
            
    except Exception as e:
        print(f"Error: {e}")
    return None

def transportVicSearch(search):
    
    url = f'https://vic.transportsg.me/metro/tracker/consist?consist={search}'
    
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    try:

        tripshtml = soup.find_all(class_='trip')
        tripshtml = [trip for trip in tripshtml if 'inactive' not in str(trip)]
        if tripshtml:
            trips = [trip.text for trip in tripshtml]
            tripsformatted = []
            for trip in trips:
                trip = trip.split(': ')
                trip.pop(0)
                temp = trip[0].split(' ',1)
                temp.append(trip[1])
                trip = temp.copy()
                tripsformatted.append(trip)
            tripsformatted

            # finding next station
        
            website = []
            for trip in tripshtml:
                soup = BeautifulSoup(str(trip),"html.parser")

                for a in soup.find_all('a', href=True):
                    website.append(f"https://vic.transportsg.me{a['href']}")
            website = website[0]

            url = website

            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            stationshtml = soup.find_all(class_='timingRow')
            stations = []
            for stationhtml in stationshtml:
                soup = BeautifulSoup(str(stationhtml),"html.parser")

                temp = []
                for a in soup.find_all('span'):
                    temp.append(a.text)
                stations.append(temp)

            departing = False
            stationsbefore = len(stations)
            stations = [station for station in stations if station[2] != '']
            if stationsbefore == len(stations):
                departing = True
                print('True')
            print(stationsbefore)
            print(len(stations))
            if stations == []:
                return 'no location data'

            try:
                station = stations[0]
            except IndexError:
                print('no location found?')
            else:
                station[0] = station[0].split(' Railway Station')[0]
                station[1] = station[1].split('Platform ')[1]
                station[2] = station[2].split(' min')[0]
                if station[2] == 'Now':
                    print(f'{search} is at {station[0]} Station on Platform {station[1]}.')
                else:
                    print(f'{search} is {station[2]} minutes away from arriving at {station[0]} Station on Platform {station[1]}.')
                return [tripsformatted,station,departing]
    
        else:
            return 'none'
    except Exception as e:
        return(f'Error: {e}')
    
def transportVicSearchStation(search,show_all):
    
    url = search.lower().replace(' ','-')
    url = f'https://vic.transportsg.me/metro/timings/{url}'
    print(url)
    
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")


    departureshtml = soup.find_all(class_='departure')

    if not departureshtml:
        print('none')
        return 'none'

    result = []
    x = -1
    for i in range(0,len(departureshtml)):
        x +=1
        if not show_all and x == 10:
            break
        print()
        print(f'{i+1}/{len(departureshtml)}')
        soup = BeautifulSoup(str(departureshtml[i]),'lxml')
        try:
            departureresult = []
            departureresult.append(soup.find(class_='bigNumber').text)
            departureresult.append(soup.find(class_='towards').text.split(' Line towards')[0])
            departureresult.append(soup.find(class_='destination').text)
            if len(soup.find(class_="timings").text.split(" min")) == 1:
                if len(soup.find(class_="timings").text.split("ow")) == 2:
                    departureresult.append("Now")
                else:
                    departureresult.append(str(int(soup.find(class_="timings").text.split(' h')[0])*60))
            elif len(soup.find(class_="timings").text.split(" min")[0].split(' h ')) == 1: 
                departureresult.append(soup.find(class_="timings").text.split(" min")[0])
            else:
                departureresult.append(str((int(soup.find(class_="timings").text.split(" min")[0].split(' h ')[0])*60)+int(soup.find(class_="timings").text.split(" min")[0].split(' h ')[1])))

            timings = soup.find(class_='timings')
            soup2 = BeautifulSoup(str(timings),'lxml')
            for a in soup2.find_all('a',href=True):
                if 'timing' in str(a['class']):
                    url = f'https://vic.transportsg.me{str(a["href"])}'
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "lxml")
            set = soup.find(class_="consist")
            if set == None:
                departureresult.append(None)
            else:
                departureresult.append(set.text)
            if departureresult == None:
                x += 1
            # departureresult.insert(2,soup.find(id='header').text.split(' to ')[1].split('Home')[0])
            result.append(departureresult)

            print(departureresult)
        except AttributeError:
            pass
    print('done')
    print(result)
    return result

def transportVicSearchLine(line):
    print(f'searching for trips on {line} line')

    url = f'https://vic.transportsg.me/metro/tracker/line?line={line.replace(' ','+')}'

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    # print(page.content)

    rareservices = []

    try:
        tripshtml = soup.find_all(class_='trip')
        tripshtml = [trip for trip in tripshtml if 'inactive' not in str(trip)] # remove trips that have finished
        if tripshtml:
            trips = [trip.text for trip in tripshtml]
            tripsformatted = []
            for trip in trips:
                trip = trip.split(': ')
                trip.pop(0)
                temp = trip[0].split(' ',1)
                temp.append(trip[1])
                trip = temp.copy()
                trip.append(checkTrainType(trip[2].split('-')[0]))
                trip.append(line)
                tripsformatted.append(trip)
            return tripsformatted
            
        else:
            return 'none'
    except Exception as e:
        print(f'Error: {e}')
        return None

def findRareServices(inputline):
    rareservices = []
    if inputline == 'all':
        for line in linelist:
            tripsforline = transportVicSearchLine(line)
            # print(tripsforline)
            if tripsforline not in ['none',None]:
                for trip in tripsforline:
                    # print(trip)
                    car = trip[2].split('-')[0]
                    
                    # print(f'trains on line: {trains_on_lines[line]}')
                    if checkTrainType(car) not in trains_on_lines[line]:
                        print('alert!')
                        print(trip)
                        print(f'car: {car}')
                        print(f'type: {checkTrainType(car)}')
                        rareservices.append(trip)
    else:
        tripsforline = transportVicSearchLine(inputline)

        for trip in tripsforline:
            # print(trip)
            car = trip[2].split('-')[0]
            
            # print(f'trains on line: {trains_on_lines[line]}')
            if checkTrainType(car) not in trains_on_lines[inputline]:
                print('alert!')
                print(trip)
                print(f'car: {car}')
                print(f'type: {checkTrainType(car)}')
                rareservices.append(trip)
    print(rareservices)
    return rareservices

# transportVicSearchStation('flinders street') 
print('\n\nyou clicked on the wrong file dumbass\n\n')