import requests
from bs4 import BeautifulSoup
import lxml
import time


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
    
def transportVicSearchStation(search):
    
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
    for i in range(0,len(departureshtml)):
        if i == 10:
            break
        print()
        print(f'{i+1}/{len(departureshtml)}')
        soup = BeautifulSoup(str(departureshtml[i]),'lxml')
        try:
            departureresult = [soup.find(class_='bigNumber').text,soup.find(class_='towards').text.split(' Line towards')[0],soup.find(class_='destination').text,f'{'Now' if len(soup.find(class_='timings').text.split(' min')) == 1 else soup.find(class_='timings').text.split(' min')[0]}']
            timings = soup.find(class_='timings')
            soup2 = BeautifulSoup(str(timings),'lxml')
            for a in soup2.find_all('a',href=True):
                if 'timing' in str(a['class']):
                    url = f'https://vic.transportsg.me{str(a['href'])}'
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "lxml")
            set = soup.find(class_="consist")
            if set == None:
                departureresult.append(None)
            else:
                departureresult.append(set.text)
            # departureresult.insert(2,soup.find(id='header').text.split(' to ')[1].split('Home')[0])
            result.append(departureresult)

            print(departureresult)
        except AttributeError:
            pass
    print('done')
    print(result)
    return result

    


# transportVicSearchStation('flinders street') 