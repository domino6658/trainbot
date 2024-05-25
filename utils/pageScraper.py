import requests
from bs4 import BeautifulSoup


def transportVicSearch(search):
    
    url = f'https://vic.transportsg.me/metro/tracker/consist?consist={search}'
    
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    try:

        trips = soup.find_all(class_='trip')
        trips = [trip for trip in trips if 'inactive' not in str(trip)]
        if trips:
            trips = [trip.text for trip in trips]
            tripsformatted = []
            for trip in trips:
                trip = trip.split(': ')
                trip.pop(0)
                temp = trip[0].split(' ',1)
                temp.append(trip[1])
                trip = temp.copy()
                tripsformatted.append(trip)
            trips = tripsformatted.copy()
            print(trips)
            return trips
        else:
            return 'none'
    except Exception as e:
        return(f'Error: {e}')

# def montagueDays(queue):
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service)
    
#     url = f'https://howmanydayssincemontaguestreetbridgehasbeenhit.com'
    
#     # Open the URL in the browser
#     driver.get(url)
    
#     try:
#         # Wait for the page to load
#         driver.implicitly_wait(5)
        
#         # Find all elements with class
#         elements = driver.find_element_by_class_name('jss25')
        
#         if elements:
#             days = elements.text
#             print(days)
#             queue.put(days)
#         else:
#             return("`Error: Number not found`")
#     except Exception as e:
#         return(f'Error: {e}')
#     finally:
#         driver.quit()