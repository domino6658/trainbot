import requests
from bs4 import BeautifulSoup


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